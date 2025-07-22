from pydantic import BaseModel, Field

from spacenote.core.comment.models import Comment
from spacenote.core.note.models import Note
from spacenote.core.space.models import Space


class ExportData(BaseModel):
    """Complete export data structure."""

    version: str = Field(default="1.0")
    space: Space
    notes: list[Note] = []
    comments: list[Comment] = []


class ImportResult(BaseModel):
    """Result of import operation."""

    space_id: str
    notes_imported: int = 0
    comments_imported: int = 0
    warnings: list[str] = []
