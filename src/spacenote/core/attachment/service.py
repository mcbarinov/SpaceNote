import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from fastapi import UploadFile
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.attachment.models import Attachment
from spacenote.core.attachment.preview import generate_preview, get_preview_path, is_image
from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError

logger = structlog.get_logger(__name__)


class AttachmentService(Service):
    """Service for managing file attachments with per-space collections."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collections: dict[str, AsyncCollection[dict[str, Any]]] = {}

    def add_collection(self, space_id: str) -> None:
        """Add a new collection for a space."""
        self._collections[space_id] = self.database.get_collection(f"{space_id}_attachments")

    async def on_start(self) -> None:
        """Initialize service on application startup."""
        for space in self.core.services.space.get_spaces():
            self._collections[space.id] = self.database.get_collection(f"{space.id}_attachments")
        logger.debug("attachment_service_started", collections_count=len(self._collections))

    async def upload_file(self, space_id: str, file: UploadFile, author: str) -> Attachment:
        """Upload a file to a space (unassigned to any note)."""
        log = logger.bind(space_id=space_id, filename=file.filename, author=author)
        log.debug("uploading_file")

        # Get the next auto-increment ID for this space
        collection = self._collections[space_id]
        last_attachment = await collection.find({}).sort("_id", -1).limit(1).to_list(1)
        next_id = 1 if not last_attachment else last_attachment[0]["_id"] + 1

        # Get the filename
        filename = file.filename or "unnamed"

        # Create attachment record
        attachment = Attachment(
            id=next_id,
            space_id=space_id,
            filename=filename,
            content_type=file.content_type or "application/octet-stream",
            size=0,  # Will be updated after saving file
            author=author,
            created_at=datetime.now(UTC),
            note_id=None,  # Unassigned
        )

        # Ensure directories exist
        attachments_root = Path(self.core.config.attachments_path)
        file_path = attachments_root / attachment.path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Read and save file content
        content = await file.read()
        file_path.write_bytes(content)

        # Update attachment with actual size
        attachment.size = len(content)

        # Save attachment record to database
        await collection.insert_one(attachment.to_dict())

        # Generate preview for images
        if is_image(attachment.content_type):
            try:
                preview_root = self.get_preview_root()
                preview_path = get_preview_path(file_path, preview_root)
                await generate_preview(file_path, preview_path)
                log.debug("preview_generated", attachment_id=attachment.id)
            except Exception as e:
                log.warning("preview_generation_failed", attachment_id=attachment.id, error=str(e))

        log.debug("file_uploaded", attachment_id=attachment.id, size=attachment.size)
        return attachment

    async def get_space_attachments(self, space_id: str, unassigned_only: bool = True) -> list[Attachment]:
        """Get attachments for a space."""
        collection = self._collections[space_id]

        query: dict[str, Any] = {}
        if unassigned_only:
            query["note_id"] = None

        cursor = collection.find(query).sort("_id", -1)
        return await Attachment.list_cursor(cursor)

    async def get_attachment(self, space_id: str, attachment_id: int) -> Attachment:
        """Get a specific attachment by ID."""
        collection = self._collections[space_id]
        doc = await collection.find_one({"_id": attachment_id})
        if not doc:
            raise NotFoundError(f"Attachment '{attachment_id}' not found in space '{space_id}'")
        return Attachment.model_validate(doc)

    def get_file_path(self, attachment: Attachment) -> Path:
        """Get the full file system path for an attachment."""
        attachments_root = Path(self.core.config.attachments_path)
        return attachments_root / attachment.path

    def get_preview_root(self) -> Path:
        """Get the preview root directory."""
        attachments_root = Path(self.core.config.attachments_path)
        return Path(f"{attachments_root}_preview")

    async def assign_to_note(self, space_id: str, attachment_id: int, note_id: int) -> Attachment:
        """Assign an attachment to a specific note."""
        log = logger.bind(space_id=space_id, attachment_id=attachment_id, note_id=note_id)
        log.debug("assigning_attachment_to_note")

        # Get the attachment
        attachment = await self.get_attachment(space_id, attachment_id)
        if attachment.note_id is not None:
            raise ValueError(f"Attachment {attachment_id} is already assigned to note {attachment.note_id}")

        # Get old path before updating the record
        attachments_root = Path(self.core.config.attachments_path)
        old_path = attachments_root / attachment.path

        # Check if the file exists
        if not old_path.exists():
            raise FileNotFoundError(f"Attachment file not found: {old_path}")

        # Update the database record
        collection = self._collections[space_id]
        await collection.update_one({"_id": attachment_id}, {"$set": {"note_id": note_id}})

        # Update attachment note_id (affects calculated path)
        attachment.note_id = note_id
        new_path = attachments_root / attachment.path

        # Create new directory structure
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(old_path), str(new_path))

        # Move preview file if it exists
        if is_image(attachment.content_type):
            preview_root = self.get_preview_root()
            old_preview_path = get_preview_path(old_path, preview_root)
            new_preview_path = get_preview_path(new_path, preview_root)

            if old_preview_path.exists():
                new_preview_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_preview_path), str(new_preview_path))
                log.debug("preview_moved_with_attachment")

        # Update the attachment count on the note
        await self.core.services.note.increment_attachment_count(space_id, note_id)

        log.debug("attachment_assigned_to_note")
        return attachment

    async def unassign_from_note(self, space_id: str, attachment_id: int) -> Attachment:
        """Unassign an attachment from its note (move back to unassigned)."""
        log = logger.bind(space_id=space_id, attachment_id=attachment_id)
        log.debug("unassigning_attachment_from_note")

        # Get the attachment
        attachment = await self.get_attachment(space_id, attachment_id)
        if attachment.note_id is None:
            raise ValueError(f"Attachment {attachment_id} is not assigned to any note")

        old_note_id = attachment.note_id

        # Get old path before updating the record
        attachments_root = Path(self.core.config.attachments_path)
        old_path = attachments_root / attachment.path

        # Check if the file exists
        if not old_path.exists():
            raise FileNotFoundError(f"Attachment file not found: {old_path}")

        # Update the database record to unassign
        collection = self._collections[space_id]
        await collection.update_one({"_id": attachment_id}, {"$set": {"note_id": None}})

        # Update attachment note_id (affects calculated path)
        attachment.note_id = None
        new_path = attachments_root / attachment.path

        # Create unassigned directory
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(old_path), str(new_path))

        # Move preview file if it exists
        if is_image(attachment.content_type):
            preview_root = self.get_preview_root()
            old_preview_path = get_preview_path(old_path, preview_root)
            new_preview_path = get_preview_path(new_path, preview_root)

            if old_preview_path.exists():
                new_preview_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_preview_path), str(new_preview_path))
                log.debug("preview_moved_with_attachment")

        # Update the attachment count on the old note
        await self.core.services.note.decrement_attachment_count(space_id, old_note_id)

        log.debug("attachment_unassigned_from_note")
        return attachment

    async def delete_attachment(self, space_id: str, attachment_id: int) -> None:
        """Delete an attachment (file and database record)."""
        log = logger.bind(space_id=space_id, attachment_id=attachment_id)
        log.debug("deleting_attachment")

        # Get the attachment first
        attachment = await self.get_attachment(space_id, attachment_id)

        # Delete the file from disk
        attachments_root = Path(self.core.config.attachments_path)
        file_path = attachments_root / attachment.path

        if file_path.exists():
            file_path.unlink()
            log.debug("attachment_file_deleted", file_path=str(file_path))
        else:
            log.warning("attachment_file_not_found", file_path=str(file_path))

        # Delete preview file if it exists
        if is_image(attachment.content_type):
            preview_root = self.get_preview_root()
            preview_path = get_preview_path(file_path, preview_root)

            if preview_path.exists():
                preview_path.unlink()
                log.debug("preview_file_deleted", preview_path=str(preview_path))
            else:
                log.debug("preview_file_not_found", preview_path=str(preview_path))

        # If attachment was assigned to a note, decrement the count
        if attachment.note_id is not None:
            await self.core.services.note.decrement_attachment_count(space_id, attachment.note_id)

        # Delete the database record
        collection = self._collections[space_id]
        await collection.delete_one({"_id": attachment_id})

        log.debug("attachment_deleted")

    async def get_note_attachments(self, space_id: str, note_id: int) -> list[Attachment]:
        """Get attachments assigned to a specific note."""
        collection = self._collections[space_id]
        cursor = collection.find({"note_id": note_id}).sort("_id", -1)
        return await Attachment.list_cursor(cursor)

    async def drop_collection(self, space_id: str) -> None:
        """Drop the entire collection for a space and cleanup files."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")

        # Delete all files
        attachments_root = Path(self.core.config.attachments_path)
        space_dir = attachments_root / space_id
        if space_dir.exists():
            shutil.rmtree(space_dir)

        # Delete all preview files
        preview_root = self.get_preview_root()
        preview_space_dir = preview_root / space_id
        if preview_space_dir.exists():
            shutil.rmtree(preview_space_dir)

        # Drop the database collection
        await self._collections[space_id].drop()
        del self._collections[space_id]
