from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from spacenote.core.attachment.models import Attachment, MediaCategory
from spacenote.core.attachment.preview import get_preview_path
from spacenote.core.comment.models import Comment
from spacenote.core.config import CoreConfig
from spacenote.core.core import Core
from spacenote.core.errors import AccessDeniedError, ValidationError
from spacenote.core.export.models import ImportResult
from spacenote.core.field.models import SpaceField
from spacenote.core.filter.models import Filter
from spacenote.core.note.models import Note, PaginationResult
from spacenote.core.session.models import Session
from spacenote.core.space.models import Space
from spacenote.core.telegram.models import TelegramBot
from spacenote.core.user.models import SessionId, User


class App:
    def __init__(self, config: CoreConfig) -> None:
        self._core = Core(config)

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None]:
        """Application lifespan management - delegates to Core."""
        async with self._core.lifespan():
            yield

    async def get_user_by_session(self, session_id: SessionId) -> User | None:
        """Get user by session ID."""
        return await self._core.services.session.get_user_by_session(session_id)

    async def is_session_valid(self, session_id: SessionId) -> bool:
        """Check if session is valid and active."""
        user = await self._core.services.session.get_user_by_session(session_id)
        return user is not None

    async def login(
        self, username: str, password: str, user_agent: str | None = None, ip_address: str | None = None
    ) -> SessionId | None:
        if not self._core.services.user.verify_password(username, password):
            return None
        return await self._core.services.session.create_session(username, user_agent, ip_address)

    async def logout(self, session_id: SessionId) -> None:
        await self._core.services.session.delete_session(session_id)

    async def get_users(self, session_id: SessionId) -> list[User]:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return self._core.services.user.get_users()

    async def create_user(self, session_id: SessionId, username: str, password: str) -> User:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.user.create_user(username, password)

    async def create_space(self, session_id: SessionId, space_id: str, name: str) -> Space:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        return await self._core.services.space.create_space(space_id, name, current_user.id)

    async def get_spaces_by_member(self, session_id: SessionId) -> list[Space]:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        return self._core.services.space.get_spaces_by_member(current_user.id)

    async def get_all_spaces(self, session_id: SessionId) -> list[Space]:
        """Get all spaces in the system."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return self._core.services.space.get_spaces()

    async def get_space(self, session_id: SessionId, space_id: str) -> Space:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        space = self._core.services.space.get_space(space_id)
        if current_user.id not in space.members:
            raise AccessDeniedError("You are not a member of this space.")
        return space

    async def add_field(self, session_id: SessionId, space_id: str, field: SpaceField) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.add_field(space_id, field)

    async def update_list_fields(self, session_id: SessionId, space_id: str, field_names: list[str]) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_list_fields(space_id, field_names)

    async def update_hidden_create_fields(self, session_id: SessionId, space_id: str, field_names: list[str]) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_hidden_create_fields(space_id, field_names)

    async def update_note_detail_template(self, session_id: SessionId, space_id: str, template: str | None) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_note_detail_template(space_id, template)

    async def update_note_list_template(self, session_id: SessionId, space_id: str, template: str | None) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_note_list_template(space_id, template)

    async def add_filter(self, session_id: SessionId, space_id: str, filter: Filter) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.add_filter(space_id, filter)

    async def delete_filter(self, session_id: SessionId, space_id: str, filter_id: str) -> None:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.delete_filter(space_id, filter_id)

    async def list_notes(
        self, session_id: SessionId, space_id: str, filter_id: str | None = None, page: int = 1, page_size: int | None = None
    ) -> PaginationResult:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)

        space = self._core.services.space.get_space(space_id)

        # Use space default page size if not specified
        if page_size is None:
            page_size = space.default_page_size

        # Enforce maximum page size
        page_size = min(page_size, space.max_page_size)

        return await self._core.services.note.list_notes(space_id, filter_id, current_user, page, page_size)

    async def create_note_from_raw_fields(self, session_id: SessionId, space_id: str, raw_fields: dict[str, str]) -> Note:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.create_note_from_raw_fields(space_id, current_user.id, raw_fields)

    async def get_note(self, session_id: SessionId, space_id: str, note_id: int) -> Note:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.get_note(space_id, note_id)

    async def export_space_as_json(self, session_id: SessionId, space_id: str, include_content: bool = False) -> dict[str, Any]:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        if not self._core.services.space.space_exists(space_id):
            raise ValidationError(f"Space '{space_id}' does not exist.")
        return await self._core.services.export.export_space(space_id, include_content)

    async def import_space_from_json(self, session_id: SessionId, data: dict[str, Any]) -> ImportResult:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.export.import_space(data, current_user.id)

    async def create_comment(self, session_id: SessionId, space_id: str, note_id: int, content: str) -> Comment:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.comment.create_comment(space_id, note_id, current_user.id, content)

    async def get_note_comments(self, session_id: SessionId, space_id: str, note_id: int) -> list[Comment]:
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.comment.get_comments_for_note(space_id, note_id)

    async def update_note_from_raw_fields(
        self, session_id: SessionId, space_id: str, note_id: int, raw_fields: dict[str, str]
    ) -> Note:
        """Update an existing note from raw field values (validates and converts)."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.note.update_note_from_raw_fields(space_id, note_id, raw_fields, current_user.id)

    async def delete_space(self, session_id: SessionId, space_id: str) -> None:
        """Delete a space and all its associated data (notes, comments). Admin only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        if not self._core.services.space.space_exists(space_id):
            raise ValidationError(f"Space '{space_id}' does not exist.")
        await self._core.services.space.delete_space(space_id)
        await self._core.services.note.drop_collection(space_id)
        await self._core.services.comment.drop_collection(space_id)
        await self._core.services.attachment.drop_collection(space_id)

    async def count_space_notes(self, session_id: SessionId, space_id: str) -> int:
        """Count the number of notes in a space. Admin only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.note.count_notes(space_id)

    async def count_space_comments(self, session_id: SessionId, space_id: str) -> int:
        """Count the number of comments in a space. Admin only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.comment.count_comments(space_id)

    async def update_space_members(self, session_id: SessionId, space_id: str, members: list[str]) -> None:
        """Update the members list for a space. Only existing members can update."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_members(space_id, members)

    async def change_password(self, session_id: SessionId, old_password: str, new_password: str) -> None:
        """Change password for the current user."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        await self._core.services.user.change_password(current_user.id, old_password, new_password)
        # Logout all sessions for security
        await self._core.services.session.delete_user_sessions(current_user.id)

    async def get_user_sessions(self, session_id: SessionId) -> list[Session]:
        """Get all active sessions for the current user."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        return await self._core.services.session.get_user_sessions(current_user.id)

    async def logout_all_sessions(self, session_id: SessionId) -> int:
        """Logout from all devices by deleting all sessions."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        return await self._core.services.session.delete_user_sessions(current_user.id)

    async def upload_attachment(self, session_id: SessionId, space_id: str, file: UploadFile) -> Attachment:
        """Upload a file attachment to a space."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.upload_file(space_id, file, current_user.id)

    async def get_space_attachments(self, session_id: SessionId, space_id: str, unassigned_only: bool = True) -> list[Attachment]:
        """Get attachments for a space."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.get_space_attachments(space_id, unassigned_only)

    async def get_media_attachments(
        self, session_id: SessionId, space_id: str, category: MediaCategory | None = None
    ) -> list[Attachment]:
        """Get media attachments (images, videos, audio) for a space."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.get_media_attachments(space_id, category)

    async def get_attachment(self, session_id: SessionId, space_id: str, attachment_id: int) -> Attachment:
        """Get a specific attachment by ID."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.get_attachment(space_id, attachment_id)

    async def get_attachment_file_path(self, session_id: SessionId, attachment: Attachment) -> Path:
        """Get the file path for an attachment."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(attachment.space_id, current_user.id)
        return self._core.services.attachment.get_file_path(attachment)

    async def get_attachment_preview_path(self, session_id: SessionId, attachment: Attachment) -> Path:
        """Get the preview file path for an attachment."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(attachment.space_id, current_user.id)

        # Get the original file path and preview root
        original_path = self._core.services.attachment.get_file_path(attachment)
        preview_root = self._core.services.attachment.get_preview_root()

        # Use the preview utility to get the preview path
        return get_preview_path(original_path, preview_root)

    async def assign_attachment_to_note(
        self, session_id: SessionId, space_id: str, attachment_id: int, note_id: int
    ) -> Attachment:
        """Assign an attachment to a specific note."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.assign_to_note(space_id, attachment_id, note_id)

    async def get_note_attachments(self, session_id: SessionId, space_id: str, note_id: int) -> list[Attachment]:
        """Get attachments for a specific note."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.get_note_attachments(space_id, note_id)

    async def unassign_attachment_from_note(self, session_id: SessionId, space_id: str, attachment_id: int) -> Attachment:
        """Unassign an attachment from its note."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        return await self._core.services.attachment.unassign_from_note(space_id, attachment_id)

    async def delete_attachment(self, session_id: SessionId, space_id: str, attachment_id: int) -> None:
        """Delete an attachment."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.attachment.delete_attachment(space_id, attachment_id)

    # Telegram Bot Management (Admin only)
    async def create_telegram_bot(self, session_id: SessionId, bot_id: str, token: str) -> TelegramBot:
        """Create a new Telegram bot. Admin only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        return await self._core.services.telegram.create_bot(bot_id, token)

    async def get_telegram_bots(self, session_id: SessionId) -> list[TelegramBot]:
        """Get all Telegram bots. Available to all authenticated users."""
        await self._core.services.access.get_authenticated_user(session_id)
        return await self._core.services.telegram.get_bots()

    async def delete_telegram_bot(self, session_id: SessionId, bot_id: str) -> None:
        """Delete a Telegram bot. Admin only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_admin(current_user.id)
        await self._core.services.telegram.delete_bot(bot_id)

    async def update_space_telegram_config(self, session_id: SessionId, space_id: str, telegram_config: dict[str, str]) -> None:
        """Update Telegram configuration for a space. Space members only."""
        current_user = await self._core.services.access.get_authenticated_user(session_id)
        self._core.services.access.ensure_space_member(space_id, current_user.id)
        await self._core.services.space.update_telegram_config(space_id, telegram_config)
