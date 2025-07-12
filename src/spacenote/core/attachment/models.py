from datetime import datetime
from pathlib import Path

from pydantic import Field

from spacenote.core.db import MongoModel


class Attachment(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    space_id: str  # Space this attachment belongs to
    filename: str  # Original filename (e.g., "report.pdf")
    content_type: str  # MIME type (e.g., "application/pdf", "image/jpeg")
    size: int  # File size in bytes
    author: str  # User who uploaded the file
    created_at: datetime  # When file was uploaded
    note_id: int | None = None  # Attached note (None = unassigned)

    @property
    def path(self) -> Path:
        """Calculate the relative path from attachments root."""
        filename_parts = Path(self.filename)
        storage_filename = f"{filename_parts.stem}__{self.id}{filename_parts.suffix}"

        if self.note_id is None:
            return Path(self.space_id) / "__unassigned__" / storage_filename
        return Path(self.space_id) / str(self.note_id) / storage_filename
