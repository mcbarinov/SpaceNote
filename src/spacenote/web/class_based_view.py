# code from https://github.com/fastapiutils/fastapi-utils/blob/master/fastapi_utils/cbv.py
import inspect
import types
from collections.abc import Callable
from typing import (
    Any,
    ClassVar,
    TypeVar,
    cast,
    get_type_hints,
)

from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from starlette.routing import Route, WebSocketRoute

T = TypeVar("T")

CBV_CLASS_KEY = "__cbv_class__"
INCLUDE_INIT_PARAMS_KEY = "__include_init_params__"
RETURN_TYPES_FUNC_KEY = "__return_types_func__"


def cbv(router: APIRouter, *urls: str) -> Callable[[type[T]], type[T]]:
    """
    This function returns a decorator that converts the decorated into a class-based view for the provided router.

    Any methods of the decorated class that are decorated as endpoints using the router provided to this function
    will become endpoints in the router. The first positional argument to the methods (typically `self`)
    will be populated with an instance created using FastAPI's dependency-injection.

    For more detail, review the documentation at
    https://fastapi-restful.netlify.app/user-guide/class-based-views//#the-cbv-decorator
    """

    def decorator(cls: type[T]) -> type[T]:
        # Define cls as cbv class exclusively when using the decorator
        return _cbv(router, cls, *urls)

    return decorator


def _cbv[T](router: APIRouter, cls: type[T], *urls: str, instance: object = None) -> type[T]:
    """
    Replaces any methods of the provided class `cls` that are endpoints of routes in `router` with updated
    function calls that will properly inject an instance of `cls`.
    """
    _init_cbv(cls, instance)
    _register_endpoints(router, cls, *urls)
    return cls


def _init_cbv(cls: type[Any], instance: object = None) -> None:
    """
    Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CBV_CLASS_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]  # drop `self` parameter
    new_parameters = [
        x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]

    dependency_names: list[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parameter_kwargs)
        )
    new_signature = inspect.Signature(())
    if not instance or hasattr(cls, INCLUDE_INIT_PARAMS_KEY):
        new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: object, *args: object, **kwargs: object) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        if instance and not hasattr(cls, INCLUDE_INIT_PARAMS_KEY):
            self.__class__ = instance.__class__
            self.__dict__ = instance.__dict__
        else:
            old_init(self, *args, **kwargs)

    cls.__signature__ = new_signature
    cls.__init__ = new_init
    setattr(cls, CBV_CLASS_KEY, True)


def _register_endpoints(router: APIRouter, cls: type[Any], *urls: str) -> None:
    cbv_router = APIRouter()
    function_members = inspect.getmembers(cls, inspect.isfunction)
    for url in urls:
        _allocate_routes_by_method_name(router, url, function_members)
    router_roles = []
    for route in router.routes:
        if not isinstance(route, APIRoute):
            raise TypeError("The provided routes should be of type APIRoute")

        route_methods: Any = route.methods
        cast(tuple[Any], route_methods)
        router_roles.append((route.path, tuple(route_methods)))

    if len(set(router_roles)) != len(router_roles):
        raise Exception("An identical route role has been implemented more then once")  # noqa: TRY002

    functions_set = {func for _, func in function_members}
    cbv_routes = [
        route for route in router.routes if isinstance(route, (Route, WebSocketRoute)) and route.endpoint in functions_set
    ]
    prefix_length = len(router.prefix)  # Until 'black' would fix an issue which causes PEP8: E203
    for route in cbv_routes:
        router.routes.remove(route)
        route.path = route.path[prefix_length:]
        _update_cbv_route_endpoint_signature(cls, route)
        route.name = cls.__name__ + "." + route.name
        cbv_router.routes.append(route)
    router.include_router(cbv_router)


def _allocate_routes_by_method_name(router: APIRouter, url: str, function_members: list[tuple[str, Any]]) -> None:
    existing_routes_endpoints: list[tuple[Any, str]] = [
        (route.endpoint, route.path) for route in router.routes if isinstance(route, APIRoute)
    ]
    for name, func in function_members:
        if hasattr(router, name) and not name.startswith("__") and not name.endswith("__"):  # noqa: SIM102
            if (func, url) not in existing_routes_endpoints:
                response_model = None
                responses = None
                kwargs = {}
                status_code = 200
                return_types_func = getattr(func, RETURN_TYPES_FUNC_KEY, None)
                if return_types_func:
                    response_model, status_code, responses, kwargs = return_types_func()

                api_resource = router.api_route(
                    url,
                    methods=[name.capitalize()],
                    response_model=response_model,
                    status_code=status_code,
                    responses=responses,
                    **kwargs,
                )
                api_resource(func)


def _update_cbv_route_endpoint_signature(cls: type[Any], route: Route | WebSocketRoute) -> None:
    """
    Fixes the endpoint signature for a cbv route to ensure FastAPI performs dependency injection properly.
    """
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_parameters: list[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]

    new_signature = old_signature.replace(parameters=new_parameters)
    route.endpoint.__signature__ = new_signature  # type:ignore[attr-defined]


def is_classvar(tp: object) -> bool:
    """Test if the type represents a class variable. Examples::

    is_classvar(int) == False
    is_classvar(ClassVar) == True
    is_classvar(ClassVar[int]) == True
    is_classvar(ClassVar[List[T]]) == True
    """

    return tp is ClassVar or (isinstance(tp, types.GenericAlias) and tp.__origin__ is ClassVar)  # type: ignore[comparison-overlap]
