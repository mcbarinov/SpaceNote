from datetime import datetime

from spacenote.core.db import MongoModel
from spacenote.core.field.models import FieldValue


class Note(MongoModel):
    id: int  # Auto-incremented within each space
    author: str
    created_at: datetime
    fields: dict[str, FieldValue]  # User-defined fields as defined in Space.fields
