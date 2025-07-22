from datetime import datetime

from pydantic import Field

from spacenote.core.db import MongoModel


class Comment(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    note_id: int  # ID of the note this comment belongs to
    author: str  # username of the comment author
    content: str  # markdown content of the comment
    created_at: datetime
    edited_at: datetime | None = None  # for future editing functionality
    parent_id: int | None = None  # for future threading functionality
