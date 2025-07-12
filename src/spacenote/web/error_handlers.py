import logging

from fastapi import Request
from fastapi.responses import HTMLResponse, Response

from spacenote.web.deps import get_app, get_render, get_session_id

logger = logging.getLogger(__name__)


async def render_error_page(request: Request, status_code: int, title: str, message: str) -> HTMLResponse:
    """Render error page using the standalone error template."""
    session_id = await get_session_id(request)
    app = await get_app(request)
    render = await get_render(request, session_id, app)
    return await render.html("error.j2", status_code=status_code, title=title, message=message)


async def access_denied_handler(request: Request, exc: Exception) -> Response:
    """Handle access denied errors (403)."""
    return await render_error_page(request=request, status_code=403, title="Access Denied", message=str(exc))


async def admin_required_handler(request: Request, exc: Exception) -> Response:
    """Handle admin required errors (403)."""
    return await render_error_page(request=request, status_code=403, title="Admin Required", message=str(exc))


async def not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle not found errors (404)."""
    return await render_error_page(request=request, status_code=404, title="Not Found", message=str(exc))


async def value_error_handler(request: Request, exc: Exception) -> Response:
    """Handle validation errors (400)."""
    return await render_error_page(request=request, status_code=400, title="Invalid Request", message=str(exc))


async def general_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle unexpected errors (500)."""
    logger.exception("Unexpected error: %s", exc)

    return await render_error_page(
        request=request, status_code=500, title="Internal Server Error", message="An unexpected error occurred."
    )
