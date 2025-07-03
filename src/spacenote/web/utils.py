from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=HTTP_303_SEE_OTHER)
