from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError
from spacenote.core.field.models import SpaceField
from spacenote.core.field.validators import validate_new_field
from spacenote.core.filter.models import Filter
from spacenote.core.filter.validators import validate_filter
from spacenote.core.space.models import Space
from spacenote.core.space.toml_operations import space_to_toml, validate_toml_import


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

    def get_space_ids(self) -> list[str]:
        """Get all space IDs from cache."""
        return list(self._spaces.keys())

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
        self.core.services.comment.add_collection(space_id)
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

    async def update_hidden_create_fields(self, space_id: str, field_names: list[str]) -> Space:
        """Update which fields are hidden in the create form."""
        space = self.get_space(space_id)

        # Validate that all field names exist and can be hidden
        for field_name in field_names:
            field = space.get_field(field_name)
            if not field:
                raise ValueError(f"Field '{field_name}' does not exist in space")

            # Check if field can be hidden (must have default if required)
            if field.required and field.default is None:
                raise ValueError(f"Field '{field_name}' is required but has no default value. Cannot hide it in create form.")

        await self._collection.update_one({"_id": space_id}, {"$set": {"hidden_create_fields": field_names}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    async def add_filter(self, space_id: str, filter: Filter) -> Space:
        """Add a new filter to space."""
        space = self.get_space(space_id)

        # Validate the filter
        errors = validate_filter(space, filter)
        if errors:
            raise ValueError("; ".join(errors))

        await self._collection.update_one({"_id": space_id}, {"$push": {"filters": filter.model_dump()}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    async def delete_filter(self, space_id: str, filter_id: str) -> Space:
        """Delete a filter from space."""
        space = self.get_space(space_id)

        # Check if filter exists
        if not space.get_filter(filter_id):
            raise NotFoundError(f"Filter '{filter_id}' not found in space '{space_id}'")

        await self._collection.update_one({"_id": space_id}, {"$pull": {"filters": {"id": filter_id}}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    def export_as_toml(self, space_id: str) -> str:
        """Export space data as TOML format."""
        space = self.get_space(space_id)
        return space_to_toml(space)

    async def import_from_toml(self, toml_content: str, member: str) -> Space:
        """Import space from TOML format with full validation before creation."""
        # Validate TOML and get structured data
        existing_space_ids = self.get_space_ids()
        import_data = validate_toml_import(toml_content, existing_space_ids)

        # Create the space
        await self.create_space(import_data.space_id, import_data.name, member)

        # Add all fields
        for field in import_data.fields:
            await self.add_field(import_data.space_id, field)

        # Update list fields if specified
        if import_data.list_fields:
            await self.update_list_fields(import_data.space_id, import_data.list_fields)

        # Update hidden create fields if specified
        if import_data.hidden_create_fields:
            await self.update_hidden_create_fields(import_data.space_id, import_data.hidden_create_fields)

        return self.get_space(import_data.space_id)

    async def delete_space(self, space_id: str) -> None:
        """Delete a space and update cache."""
        if not self.space_exists(space_id):
            raise NotFoundError(f"Space '{space_id}' not found")
        await self._collection.delete_one({"_id": space_id})
        del self._spaces[space_id]
        # Note and Comment collections cleanup will be handled by the App layer

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
