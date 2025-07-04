from pydantic import Field

from spacenote.core.db import MongoModel
from spacenote.core.field.models import SpaceField


class Space(MongoModel):
    id: str = Field(alias="_id")  # Globally unique slug, e.g. "our-tasks", "my-journal"
    name: str
    members: list[str] = []  # users who have full access to this space
    fields: list[SpaceField] = []  # Custom fields, order matters for UI display
    list_fields: list[str] = []  # Default field names to show in notes list (can be overridden by filters)

    def get_field(self, field_name: str) -> SpaceField | None:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None
