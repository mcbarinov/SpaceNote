from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.config import CoreConfig

if TYPE_CHECKING:
    from spacenote.core.access.service import AccessService
    from spacenote.core.space.service import SpaceService
    from spacenote.core.user.service import UserService


class Service:
    """New base class for services with direct database access."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        self.database = database
        self._core: Core | None = None

    @property
    def core(self) -> Core:
        """Get the core application context."""
        if self._core is None:
            raise RuntimeError("Core not set for service")
        return self._core

    def set_core(self, core: Core) -> None:
        """Set the core application context."""
        self._core = core


class Services:
    user: UserService
    space: SpaceService
    access: AccessService

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        from spacenote.core.access.service import AccessService  # noqa: PLC0415
        from spacenote.core.space.service import SpaceService  # noqa: PLC0415
        from spacenote.core.user.service import UserService  # noqa: PLC0415

        self.user = UserService(database)
        self.space = SpaceService(database)
        self.access = AccessService(database)

    def set_core(self, core: Core) -> None:
        """Set core reference for all services."""
        self.user.set_core(core)
        self.space.set_core(core)
        self.access.set_core(core)


class Core:
    """Core application class that manages the lifecycle and database."""

    mongo_client: AsyncMongoClient[dict[str, Any]]
    database: AsyncDatabase[dict[str, Any]]
    services: Services

    def __init__(self, config: CoreConfig) -> None:
        """Initialize the core application with configuration."""
        self.mongo_client = AsyncMongoClient(config.database_url)
        self.database = self.mongo_client.get_database(urlparse(config.database_url).path[1:])
        self.services = Services(self.database)
        self.services.set_core(self)

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None]:
        await self.on_start()
        try:
            yield
        finally:
            await self.on_stop()

    async def on_start(self) -> None:
        """Initialize the application on startup."""
        await self.services.user.update_cache()
        await self.services.user.ensure_admin_user_exists()
        await self.services.space.update_cache()

    async def on_stop(self) -> None:
        """Cleanup on application shutdown."""
        await self.mongo_client.aclose()
