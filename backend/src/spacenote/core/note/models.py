from dataclasses import dataclass
from datetime import datetime

from pydantic import Field

from spacenote.core.attachment.models import AttachmentCounts
from spacenote.core.db import MongoModel
from spacenote.core.field.models import FieldValueType


@dataclass
class PaginationResult:
    """Result of a paginated query."""

    notes: list["Note"]
    total_count: int
    current_page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class Note(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    author: str
    created_at: datetime
    edited_at: datetime | None = None  # Last time note fields were edited
    fields: dict[str, FieldValueType]  # User-defined fields as defined in Space.fields
    comment_count: int = 0  # Number of comments on this note
    last_comment_at: datetime | None = None  # Date of the most recent comment
    attachment_counts: AttachmentCounts = AttachmentCounts()  # Categorized attachment counts
