from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request

from spacenote.core.app import App
from spacenote.core.user.models import SessionId


async def get_app(request: Request) -> App:
    return cast(App, request.app.state.app)


async def get_session_id(request: Request) -> SessionId | None:
    """Get session ID from headers or cookies."""
    # Check X-Session-ID header first (for development)
    session_header = request.headers.get("x-session-id")
    if session_header:
        return SessionId(session_header)

    # Fallback to cookies (for future production use)
    session_id = request.cookies.get("session_id")
    if session_id:
        return SessionId(session_id)
    return None


async def require_session_id(session_id: Annotated[SessionId | None, Depends(get_session_id)]) -> SessionId:
    """Require valid session ID for API calls."""
    if session_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session_id


class ApiView:
    """View for API endpoints that need SessionId for authentication."""

    app: App = Depends(get_app)
    session_id: SessionId = Depends(require_session_id)
