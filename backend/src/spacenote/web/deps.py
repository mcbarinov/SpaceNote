from typing import Annotated, cast

from fastapi import Depends, Request

from spacenote.core.app import App
from spacenote.core.errors import AuthenticationError
from spacenote.core.user.models import SessionId


async def get_app(request: Request) -> App:
    return cast(App, request.app.state.app)


async def get_session_id(request: Request) -> SessionId:
    """Get and validate session ID, raise AuthenticationError if invalid."""
    app = cast(App, request.app.state.app)

    # Check X-Session-ID header first (for development)
    session_header = request.headers.get("x-session-id")
    if session_header:
        session_id = SessionId(session_header)
        if await app.is_session_valid(session_id):
            return session_id

    # Fallback to cookies (for future production use)
    session_cookie = request.cookies.get("session_id")
    if session_cookie:
        session_id = SessionId(session_cookie)
        if await app.is_session_valid(session_id):
            return session_id

    raise AuthenticationError("Valid session required")


# Type aliases for dependencies
AppDep = Annotated[App, Depends(get_app)]
SessionIdDep = Annotated[SessionId, Depends(get_session_id)]
