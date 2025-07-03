from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request
from jinja2 import Environment

from spacenote.core.app import App
from spacenote.core.user.models import User
from spacenote.web.render import Render


async def get_app(request: Request) -> App:
    return cast(App, request.app.state.app)


async def get_current_user(request: Request, app: Annotated[App, Depends(get_app)]) -> User | None:
    """Get current authenticated user from session."""
    session_id = request.cookies.get("session_id")
    if session_id:
        return await app.get_user_by_session(session_id)
    return None


async def require_auth_for_view(current_user: Annotated[User | None, Depends(get_current_user)]) -> User:
    """Require authenticated user for view, redirect if not authenticated."""
    if current_user is None:
        raise HTTPException(status_code=302, detail="Authentication required", headers={"Location": "/login"})
    return current_user


async def get_render(request: Request, current_user: Annotated[User | None, Depends(get_current_user)]) -> Render:
    jinja_env = cast(Environment, request.app.state.jinja_env)
    return Render(jinja_env, request, current_user)


class AuthView:
    app: App = Depends(get_app)
    render: Render = Depends(get_render)
    current_user: User | None = Depends(get_current_user)


class View:
    app: App = Depends(get_app)
    render: Render = Depends(get_render)
    current_user: User = Depends(require_auth_for_view)
