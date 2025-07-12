from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from spacenote.core.app import App
from spacenote.core.errors import AccessDeniedError, AdminRequiredError, NotFoundError
from spacenote.web.config import WebConfig
from spacenote.web.error_handlers import (
    access_denied_handler,
    admin_required_handler,
    general_exception_handler,
    not_found_handler,
    value_error_handler,
)
from spacenote.web.render import init_jinja
from spacenote.web.routers.admin import router as admin_router
from spacenote.web.routers.api import router as api_router
from spacenote.web.routers.attachment import router as attachment_router
from spacenote.web.routers.auth import router as auth_router
from spacenote.web.routers.media import router as media_router
from spacenote.web.routers.note import router as note_router
from spacenote.web.routers.profile import router as profile_router
from spacenote.web.routers.space import router as space_router


def create_fastapi_app(app_instance: App, web_config: WebConfig) -> FastAPI:
    """Create and configure FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        """FastAPI application lifespan management."""
        # Store app instance in app state
        app.state.jinja_env = init_jinja()
        app.state.app = app_instance
        async with app_instance.lifespan():
            yield

    app = FastAPI(title="SpaceNote", version=version("spacenote"), lifespan=lifespan)

    app.add_middleware(SessionMiddleware, secret_key=web_config.session_secret_key)

    # Health check endpoint for Docker
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(note_router)
    app.include_router(space_router)
    app.include_router(attachment_router)
    app.include_router(media_router)
    app.include_router(profile_router)
    app.include_router(api_router)

    # Register error handlers
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
    app.add_exception_handler(AdminRequiredError, admin_required_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app
