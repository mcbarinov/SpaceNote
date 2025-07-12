import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from fastapi import UploadFile
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.attachment.models import Attachment
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

        # Determine file extension
        filename = file.filename or "unnamed"
        file_extension = Path(filename).suffix

        # Create attachment record
        attachment = Attachment(
            id=next_id,
            space_id=space_id,
            filename=filename,
            content_type=file.content_type or "application/octet-stream",
            size=0,  # Will be updated after saving file
            path="",  # Will be set after saving file
            author=author,
            created_at=datetime.now(UTC),
            note_id=None,  # Unassigned
        )

        # Ensure directories exist
        attachments_root = Path(self.core.config.attachments_path)
        space_dir = attachments_root / space_id
        unassigned_dir = space_dir / "__unassigned__"
        unassigned_dir.mkdir(parents=True, exist_ok=True)

        # Save file to disk
        storage_filename = f"{filename}__{next_id}{file_extension}"
        file_path = unassigned_dir / storage_filename

        # Read and save file content
        content = await file.read()
        file_path.write_bytes(content)

        # Update attachment with actual size and path
        attachment.size = len(content)
        attachment.path = f"{space_id}/__unassigned__/{storage_filename}"

        # Save attachment record to database
        await collection.insert_one(attachment.to_dict())

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

    async def drop_collection(self, space_id: str) -> None:
        """Drop the entire collection for a space and cleanup files."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")

        # Delete all files
        attachments_root = Path(self.core.config.attachments_path)
        space_dir = attachments_root / space_id
        if space_dir.exists():
            shutil.rmtree(space_dir)

        # Drop the database collection
        await self._collections[space_id].drop()
        del self._collections[space_id]
