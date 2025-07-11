from datetime import datetime

from pydantic import Field

from spacenote.core.db import MongoModel


class Attachment(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    space_id: str  # Space this attachment belongs to
    filename: str  # Original filename (e.g., "report.pdf")
    content_type: str  # MIME type (e.g., "application/pdf", "image/jpeg")
    size: int  # File size in bytes
    path: str  # Relative path from attachments root
    author: str  # User who uploaded the file
    created_at: datetime  # When file was uploaded
    note_id: int | None = None  # Attached note (None = unassigned)
