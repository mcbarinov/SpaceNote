from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request
from jinja2 import Environment

from spacenote.core.app import App
from spacenote.core.user.models import SessionId, User
from spacenote.web.render import Render


async def get_app(request: Request) -> App:
    return cast(App, request.app.state.app)


async def get_session_id(request: Request) -> SessionId | None:
    """Get session ID from cookies."""
    session_id = request.cookies.get("session_id")
    if session_id:
        return SessionId(session_id)
    return None


async def require_session_id(session_id: Annotated[SessionId | None, Depends(get_session_id)]) -> SessionId:
    """Require valid session ID for API calls."""
    if session_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session_id


async def get_render(
    request: Request, session_id: Annotated[SessionId | None, Depends(get_session_id)], app: Annotated[App, Depends(get_app)]
) -> Render:
    jinja_env = cast(Environment, request.app.state.jinja_env)
    current_user: User | None = None
    if session_id:
        current_user = await app.get_user_by_session(session_id)
    return Render(jinja_env, request, current_user)


class ApiView:
    """View for API endpoints that need SessionId for authentication."""

    app: App = Depends(get_app)
    session_id: SessionId = Depends(require_session_id)


class SessionView:
    """View for web pages that need SessionId and render."""

    app: App = Depends(get_app)
    render: Render = Depends(get_render)
    session_id: SessionId = Depends(require_session_id)
