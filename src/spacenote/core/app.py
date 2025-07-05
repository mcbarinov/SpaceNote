from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from spacenote.core.config import CoreConfig
from spacenote.core.core import Core
from spacenote.core.errors import AccessDeniedError, AdminRequiredError
from spacenote.core.field.models import SpaceField
from spacenote.core.note.models import Note
from spacenote.core.space.models import Space
from spacenote.core.user.models import User


class App:
    def __init__(self, config: CoreConfig) -> None:
        self._core = Core(config)

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None]:
        """Application lifespan management - delegates to Core."""
        async with self._core.lifespan():
            yield

    async def get_user_by_session(self, session_id: str) -> User | None:
        return self._core.services.user.get_user_by_session(session_id)

    async def login(self, username: str, password: str) -> str | None:
        return await self._core.services.user.login(username, password)

    async def logout(self, session_id: str) -> None:
        user = self._core.services.user.get_user_by_session(session_id)
        if user:
            await self._core.services.user.logout(user.id)

    def get_users(self, current_user: User) -> list[User]:
        if not current_user.admin:
            raise AdminRequiredError
        return self._core.services.user.get_users()

    async def create_user(self, current_user: User, username: str, password: str) -> User:
        if not current_user.admin:
            raise AdminRequiredError
        return await self._core.services.user.create_user(username, password, admin=False)

    async def create_space(self, current_user: User, space_id: str, name: str) -> Space:
        return await self._core.services.space.create_space(space_id, name, current_user.id)

    def get_spaces_by_member(self, current_user: User) -> list[Space]:
        return self._core.services.space.get_spaces_by_member(current_user.id)

    def get_space(self, current_user: User, space_id: str) -> Space:
        space = self._core.services.space.get_space(space_id)
        if current_user.id not in space.members:
            raise AccessDeniedError("You are not a member of this space.")
        return space

    async def add_field(self, current_user: User, space_id: str, field: SpaceField) -> None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.add_field(space_id, field)

    async def update_list_fields(self, current_user: User, space_id: str, field_names: list[str]) -> None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_list_fields(space_id, field_names)

    async def list_notes(self, current_user: User, space_id: str) -> list[Note]:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.list_notes(space_id)

    async def create_note_from_raw_fields(self, current_user: User, space_id: str, raw_fields: dict[str, str]) -> Note:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.create_note_from_raw_fields(space_id, current_user.id, raw_fields)

    async def get_note(self, current_user: User, space_id: str, note_id: int) -> Note | None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.get_note(space_id, note_id)

    def export_space_as_toml(self, current_user: User, space_id: str) -> str:
        """Export space data as TOML format."""
        # Verify user has access to the space
        self.get_space(current_user, space_id)
        # Export space data
        return self._core.services.space.export_as_toml(space_id)
