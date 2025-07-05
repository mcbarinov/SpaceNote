from typing import Any

import tomli_w
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError
from spacenote.core.field.models import FieldOption, FieldOptionValueType, FieldValueType, SpaceField
from spacenote.core.field.validators import validate_new_field
from spacenote.core.space.models import Space


class SpaceService(Service):
    """Service for managing spaces with in-memory caching."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collection = database.get_collection("spaces")
        self._spaces: dict[str, Space] = {}

    def get_space(self, id: str) -> Space:
        """Get space by ID from cache."""
        if id not in self._spaces:
            raise NotFoundError(f"Space '{id}' not found")
        return self._spaces[id]

    def space_exists(self, id: str) -> bool:
        """Check if space exists in cache."""
        return id in self._spaces

    def get_spaces(self) -> list[Space]:
        """Get all spaces from cache."""
        return list(self._spaces.values())

    def get_spaces_by_member(self, member: str) -> list[Space]:
        """Get all spaces where the user is a member."""
        return [space for space in self._spaces.values() if member in space.members]

    async def create_space(self, space_id: str, name: str, member: str) -> Space:
        """Create a new space with validation."""
        if not space_id or not space_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Space ID must be a valid slug (alphanumeric with hyphens/underscores)")
        if self.space_exists(space_id):
            raise ValueError(f"Space with ID '{space_id}' already exists")

        await self._collection.insert_one(Space(id=space_id, name=name, members=[member]).to_dict())
        await self.update_cache(space_id)
        self.core.services.note.add_collection(space_id)
        return self.get_space(space_id)

    async def update_members(self, space_id: str, members: list[str]) -> Space:
        """Update space members"""
        if not self.space_exists(space_id):
            raise NotFoundError(f"Space '{space_id}' not found")
        for member in members:
            if not self.core.services.user.user_exists(member):
                raise ValueError(f"User '{member}' does not exist")

        await self._collection.update_one({"_id": space_id}, {"$set": {"members": members}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    async def add_field(self, space_id: str, field: SpaceField) -> Space:
        """Add a new field to space."""
        space = self.get_space(space_id)
        validated_field = validate_new_field(space, field)

        await self._collection.update_one({"_id": space_id}, {"$push": {"fields": validated_field.model_dump()}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    async def update_list_fields(self, space_id: str, field_names: list[str]) -> Space:
        """Update which fields are shown in the notes list."""
        space = self.get_space(space_id)

        # Validate that all field names exist
        existing_field_names = {field.name for field in space.fields}
        for field_name in field_names:
            if field_name not in existing_field_names:
                raise ValueError(f"Field '{field_name}' does not exist in space")

        await self._collection.update_one({"_id": space_id}, {"$set": {"list_fields": field_names}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    def export_as_toml(self, space_id: str) -> str:
        """Export space data as TOML format."""
        space = self.get_space(space_id)

        # Convert space to dict for TOML serialization
        fields_list: list[dict[str, str | bool | dict[FieldOption, FieldOptionValueType] | FieldValueType]] = []
        space_dict = {
            "id": space.id,
            "name": space.name,
            "members": space.members,
            "list_fields": space.list_fields,
            "fields": fields_list,
        }

        # Convert fields to dict format
        for field in space.fields:
            field_dict: dict[str, str | bool | dict[FieldOption, FieldOptionValueType] | FieldValueType] = {
                "name": field.name,
                "type": field.type.value,
                "required": field.required,
            }
            # Only add non-None values
            if field.options:
                field_dict["options"] = field.options
            if field.default is not None:
                field_dict["default"] = field.default
            fields_list.append(field_dict)

        # Convert to TOML format
        return tomli_w.dumps(space_dict)

    async def update_cache(self, id: str | None = None) -> None:
        """Reload spaces cache from database."""
        if id is not None:  # update a specific space
            user = await self._collection.find_one({"_id": id})
            if user is None:
                del self._spaces[id]
            self._spaces[id] = Space.model_validate(user)
        else:  # update all spaces
            spaces = await Space.list_cursor(self._collection.find())
            self._spaces = {space.id: space for space in spaces}

    async def on_start(self) -> None:
        return await self.update_cache()
