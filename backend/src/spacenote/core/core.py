from __future__ import annotations

import importlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import urlparse

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.config import CoreConfig
from spacenote.core.logging import setup_logging

if TYPE_CHECKING:
    from spacenote.core.access.service import AccessService
    from spacenote.core.attachment.service import AttachmentService
    from spacenote.core.comment.service import CommentService
    from spacenote.core.export.service import ExportService
    from spacenote.core.note.service import NoteService
    from spacenote.core.session.service import SessionService
    from spacenote.core.space.service import SpaceService
    from spacenote.core.special.service import SpecialService
    from spacenote.core.telegram.service import TelegramService
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
    """Service registry that automatically discovers and initializes services."""

    user: UserService
    space: SpaceService
    comment: CommentService
    access: AccessService
    note: NoteService
    export: ExportService
    attachment: AttachmentService
    telegram: TelegramService
    session: SessionService
    special: SpecialService

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        """Initialize all services automatically using service configuration."""
        self._services: list[Service] = []
        self._database = database

        # Service configuration: (attribute_name, module_path, class_name)
        # Order matters for initialization - user and space must be first
        service_configs = [
            ("user", "spacenote.core.user.service", "UserService"),
            ("space", "spacenote.core.space.service", "SpaceService"),
            ("access", "spacenote.core.access.service", "AccessService"),
            ("session", "spacenote.core.session.service", "SessionService"),
            ("note", "spacenote.core.note.service", "NoteService"),
            ("comment", "spacenote.core.comment.service", "CommentService"),
            ("attachment", "spacenote.core.attachment.service", "AttachmentService"),
            ("export", "spacenote.core.export.service", "ExportService"),
            ("special", "spacenote.core.special.service", "SpecialService"),
            ("telegram", "spacenote.core.telegram.service", "TelegramService"),
        ]

        # Dynamically import and instantiate services
        for attr_name, module_path, class_name in service_configs:
            module = importlib.import_module(module_path)
            service_class = cast(type[Service], getattr(module, class_name))
            service_instance = service_class(database)
            setattr(self, attr_name, service_instance)
            self._services.append(service_instance)

    def set_core(self, core: Core) -> None:
        """Set core reference for all services."""
        for service in self._services:
            service.set_core(core)

    async def start_all(self) -> None:
        """Start all services that have startup logic."""
        for service in self._services:
            if hasattr(service, "on_start"):
                await service.on_start()

    async def stop_all(self) -> None:
        """Stop all services that have cleanup logic."""
        for service in self._services:
            if hasattr(service, "on_stop"):
                await service.on_stop()


class Core:
    """Core application class that manages the lifecycle and database."""

    config: CoreConfig
    mongo_client: AsyncMongoClient[dict[str, Any]]
    database: AsyncDatabase[dict[str, Any]]
    services: Services

    def __init__(self, config: CoreConfig) -> None:
        """Initialize the core application with configuration."""
        # Setup logging first
        setup_logging(config)

        self.config = config
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
        await self.services.start_all()

    async def on_stop(self) -> None:
        """Cleanup on application shutdown."""
        await self.services.stop_all()
        await self.mongo_client.aclose()
