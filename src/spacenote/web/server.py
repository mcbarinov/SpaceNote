from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from spacenote.core.app import App
from spacenote.web.config import WebConfig
from spacenote.web.render import init_jinja
from spacenote.web.routers.admin import router as admin_router
from spacenote.web.routers.auth import router as auth_router
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

    app = FastAPI(title="SpaceNote", version="0.1.0", lifespan=lifespan)

    app.add_middleware(SessionMiddleware, secret_key=web_config.session_secret_key)

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(note_router)
    app.include_router(space_router)
    app.include_router(profile_router)

    return app
