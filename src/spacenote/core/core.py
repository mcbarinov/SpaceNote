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
    from spacenote.core.comment.service import CommentService
    from spacenote.core.export.service import ExportService
    from spacenote.core.note.service import NoteService
    from spacenote.core.space.service import SpaceService
    from spacenote.core.user.service import UserService


class Service:
    """Base class for services with direct database access."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        self.database = database
        self._core: Core | None = None

    async def on_start(self) -> None:
        """Initialize service on application startup."""

    async def on_stop(self) -> None:
        """Cleanup service on application shutdown."""

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
    comment: CommentService
    access: AccessService
    note: NoteService
    export: ExportService

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        from spacenote.core.access.service import AccessService  # noqa: PLC0415
        from spacenote.core.comment.service import CommentService  # noqa: PLC0415
        from spacenote.core.export.service import ExportService  # noqa: PLC0415
        from spacenote.core.note.service import NoteService  # noqa: PLC0415
        from spacenote.core.space.service import SpaceService  # noqa: PLC0415
        from spacenote.core.user.service import UserService  # noqa: PLC0415

        self.user = UserService(database)
        self.space = SpaceService(database)
        self.comment = CommentService(database)
        self.access = AccessService(database)
        self.note = NoteService(database)
        self.export = ExportService(database)

    def set_core(self, core: Core) -> None:
        """Set core reference for all services."""
        self.user.set_core(core)
        self.space.set_core(core)
        self.comment.set_core(core)
        self.access.set_core(core)
        self.note.set_core(core)
        self.export.set_core(core)


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
        await self.services.user.on_start()
        await self.services.space.on_start()
        await self.services.comment.on_start()
        await self.services.note.on_start()

    async def on_stop(self) -> None:
        """Cleanup on application shutdown."""
        await self.mongo_client.aclose()
