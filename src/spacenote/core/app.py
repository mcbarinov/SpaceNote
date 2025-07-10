from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from spacenote.core.comment.models import Comment
from spacenote.core.config import CoreConfig
from spacenote.core.core import Core
from spacenote.core.errors import AccessDeniedError
from spacenote.core.export.models import ImportResult
from spacenote.core.field.models import SpaceField
from spacenote.core.filter.models import Filter
from spacenote.core.note.models import Note, PaginationResult
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
        self._core.services.access.ensure_admin(current_user.id)
        return self._core.services.user.get_users()

    async def create_user(self, current_user: User, username: str, password: str) -> User:
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.user.create_user(username, password)

    async def create_space(self, current_user: User, space_id: str, name: str) -> Space:
        return await self._core.services.space.create_space(space_id, name, current_user.id)

    def get_spaces_by_member(self, current_user: User) -> list[Space]:
        return self._core.services.space.get_spaces_by_member(current_user.id)

    def get_all_spaces(self, current_user: User) -> list[Space]:
        """Get all spaces in the system."""
        self._core.services.access.ensure_admin(current_user.id)
        return self._core.services.space.get_spaces()

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

    async def update_hidden_create_fields(self, current_user: User, space_id: str, field_names: list[str]) -> None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_hidden_create_fields(space_id, field_names)

    async def add_filter(self, current_user: User, space_id: str, filter: Filter) -> None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.add_filter(space_id, filter)

    async def delete_filter(self, current_user: User, space_id: str, filter_id: str) -> None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.delete_filter(space_id, filter_id)

    async def list_notes(
        self, current_user: User, space_id: str, filter_id: str | None = None, page: int = 1, page_size: int | None = None
    ) -> PaginationResult:
        self._core.services.access.ensure_space_member(space_id, current_user.id)

        space = self._core.services.space.get_space(space_id)

        # Use space default page size if not specified
        if page_size is None:
            page_size = space.default_page_size

        # Enforce maximum page size
        page_size = min(page_size, space.max_page_size)

        return await self._core.services.note.list_notes(space_id, filter_id, current_user, page, page_size)

    async def create_note_from_raw_fields(self, current_user: User, space_id: str, raw_fields: dict[str, str]) -> Note:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.create_note_from_raw_fields(space_id, current_user.id, raw_fields)

    async def get_note(self, current_user: User, space_id: str, note_id: int) -> Note | None:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.get_note(space_id, note_id)

    async def export_space_as_json(self, current_user: User, space_id: str, include_content: bool = False) -> dict[str, Any]:
        self._core.services.access.ensure_admin(current_user.id)
        self.get_space(current_user, space_id)
        return await self._core.services.export.export_space(space_id, include_content)

    async def import_space_from_json(self, current_user: User, data: dict[str, Any]) -> ImportResult:
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.export.import_space(data, current_user.id)

    async def create_comment(self, current_user: User, space_id: str, note_id: int, content: str) -> Comment:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.comment.create_comment(space_id, note_id, current_user.id, content)

    async def get_note_comments(self, current_user: User, space_id: str, note_id: int) -> list[Comment]:
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.comment.get_comments_for_note(space_id, note_id)

    async def update_note_from_raw_fields(
        self, current_user: User, space_id: str, note_id: int, raw_fields: dict[str, str]
    ) -> Note:
        """Update an existing note from raw field values (validates and converts)."""
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.update_note_from_raw_fields(space_id, note_id, raw_fields)

    async def delete_space(self, current_user: User, space_id: str) -> None:
        """Delete a space and all its associated data (notes, comments). Admin only."""
        self._core.services.access.ensure_admin(current_user.id)
        if not self._core.services.space.space_exists(space_id):
            raise ValueError(f"Space '{space_id}' does not exist.")
        await self._core.services.space.delete_space(space_id)
        await self._core.services.note.drop_collection(space_id)
        await self._core.services.comment.drop_collection(space_id)

    async def count_space_notes(self, current_user: User, space_id: str) -> int:
        """Count the number of notes in a space. Admin only."""
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.note.count_notes(space_id)

    async def count_space_comments(self, current_user: User, space_id: str) -> int:
        """Count the number of comments in a space. Admin only."""
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.comment.count_comments(space_id)

    async def update_space_members(self, current_user: User, space_id: str, members: list[str]) -> None:
        """Update the members list for a space. Only existing members can update."""
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_members(space_id, members)

    async def change_password(self, current_user: User, old_password: str, new_password: str) -> None:
        """Change password for the current user."""
        await self._core.services.user.change_password(current_user.id, old_password, new_password)
