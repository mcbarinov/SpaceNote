import logging

from fastapi import Request
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


def create_json_error_response(status_code: int, title: str, message: str) -> JSONResponse:
    """Create JSON error response."""
    return JSONResponse(status_code=status_code, content={"error": title, "detail": message, "status_code": status_code})


async def access_denied_handler(_: Request, exc: Exception) -> Response:
    """Handle access denied errors (403)."""
    return create_json_error_response(status_code=403, title="Access Denied", message=str(exc))


async def admin_required_handler(_: Request, exc: Exception) -> Response:
    """Handle admin required errors (403)."""
    return create_json_error_response(status_code=403, title="Admin Required", message=str(exc))


async def not_found_handler(_: Request, exc: Exception) -> Response:
    """Handle not found errors (404)."""
    return create_json_error_response(status_code=404, title="Not Found", message=str(exc))


async def value_error_handler(_: Request, exc: Exception) -> Response:
    """Handle validation errors (400)."""
    return create_json_error_response(status_code=400, title="Invalid Request", message=str(exc))


async def authentication_error_handler(_: Request, exc: Exception) -> Response:
    """Handle authentication errors."""
    return JSONResponse(status_code=401, content={"error": "Authentication Required", "detail": str(exc), "status_code": 401})


async def general_exception_handler(_: Request, exc: Exception) -> Response:
    """Handle unexpected errors (500)."""
    logger.exception("Unexpected error: %s", exc)
    return create_json_error_response(status_code=500, title="Internal Server Error", message="An unexpected error occurred.")
