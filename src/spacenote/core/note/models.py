from datetime import datetime

from pydantic import Field

from spacenote.core.db import MongoModel
from spacenote.core.field.models import FieldValueType


class Note(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    author: str
    created_at: datetime
    fields: dict[str, FieldValueType]  # User-defined fields as defined in Space.fields
