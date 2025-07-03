from pydantic import Field

from spacenote.core.db import MongoModel
from spacenote.core.field.models import SpaceField
from spacenote.core.filter.models import Filter


class Space(MongoModel):
    id: str = Field(alias="_id")  # Globally unique slug, e.g. "our-tasks", "my-journal"
    name: str
    members: list[str] = []  # users who have full access to this space
    fields: list[SpaceField] = []  # Custom fields, order matters for UI display
    list_fields: list[str] = []  # Default field names to show in notes list (can be overridden by filters)
    hidden_create_fields: list[str] = []  # Field names to hide in create form
    filters: list[Filter] = []  # Filter definitions for this space
    default_page_size: int = 20  # Default number of records per page
    max_page_size: int = 100  # Maximum allowed page size

    def get_field(self, field_name: str) -> SpaceField | None:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None

    def get_filter(self, filter_id: str) -> Filter | None:
        """Get filter definition by ID."""
        for filter in self.filters:
            if filter.id == filter_id:
                return filter
        return None
