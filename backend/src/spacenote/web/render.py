from collections.abc import Sequence
from importlib.metadata import version

from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2 import ChoiceLoader, Environment, PackageLoader
from markupsafe import Markup

from spacenote.core.field.models import FieldType
from spacenote.core.user.models import User


def empty(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, Sequence) and len(value) == 0:
        return ""
    return value


def yes_no(
    value: object, is_colored: bool = True, hide_no: bool = False, none_is_false: bool = False, on_off: bool = False
) -> Markup:
    clr = "black"
    if none_is_false and value is None:
        value = False

    if value is True:
        value = "on" if on_off else "yes"
        clr = "green"
    elif value is False:
        value = "" if hide_no else "off" if on_off else "no"
        clr = "red"
    elif value is None:
        value = ""
    if not is_colored:
        clr = "black"
    return Markup(f"<span style='color: {clr};'>{value}</span>")  # nosec  # noqa: S704


def init_jinja() -> Environment:
    loader = ChoiceLoader([PackageLoader("spacenote.web")])
    env = Environment(loader=loader, autoescape=True, enable_async=True)

    env.filters |= {"empty": empty, "yes_no": yes_no}
    env.globals |= {"field_types": list(FieldType), "version": version("spacenote")}
    return env


class Render:
    def __init__(self, env: Environment, request: Request, current_user: User | None = None) -> None:
        self.env = env
        self.request = request
        self.current_user = current_user

    async def html(self, template_name: str, **kwargs: object) -> HTMLResponse:
        flash_messages = self.request.session.pop("flash_messages") if "flash_messages" in self.request.session else []

        # Automatically inject current_user into template context
        context = {"flash_messages": flash_messages, "current_user": self.current_user} | kwargs

        html_content = await self.env.get_template(template_name).render_async(context)
        return HTMLResponse(content=html_content, status_code=200)

    def flash(self, message: str, is_error: bool = False) -> None:
        if "flash_messages" not in self.request.session:
            self.request.session["flash_messages"] = []
        self.request.session["flash_messages"].append({"message": message, "error": is_error})
