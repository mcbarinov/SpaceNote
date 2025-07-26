from typing import Any

import structlog
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.errors import NotFoundError, ValidationError
from spacenote.core.field.models import SpaceField
from spacenote.core.field.validators import validate_new_field
from spacenote.core.filter.models import Filter
from spacenote.core.filter.validators import validate_filter
from spacenote.core.space.json_operations import space_to_json, validate_json_import
from spacenote.core.space.models import Space
from spacenote.core.telegram.models import TelegramConfig

logger = structlog.get_logger(__name__)


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
        log = logger.bind(space_id=space_id, member=member, action="create_space")
        log.debug("creating_space")

        if not space_id or not space_id.replace("-", "").replace("_", "").isalnum():
            log.warning("invalid_space_id")
            raise ValidationError("Space ID must be a valid slug (alphanumeric with hyphens/underscores)")
        if self.space_exists(space_id):
            log.warning("space_already_exists")
            raise ValidationError(f"Space with ID '{space_id}' already exists")

        await self._collection.insert_one(Space(id=space_id, name=name, members=[member]).to_dict())
        await self.update_cache(space_id)
        self.core.services.note.add_collection(space_id)
        self.core.services.comment.add_collection(space_id)
        self.core.services.attachment.add_collection(space_id)

        log.debug("space_created", name=name)
        return self.get_space(space_id)

    async def update_members(self, space_id: str, members: list[str]) -> Space:
        """Update space members"""
        if not self.space_exists(space_id):
            raise NotFoundError(f"Space '{space_id}' not found")
        for member in members:
            if not self.core.services.user.user_exists(member):
                raise ValidationError(f"User '{member}' does not exist")

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

        # System fields that are always available
        system_fields = {"id", "author", "created_at"}

        # Validate that all field names exist
        existing_field_names = {field.name for field in space.fields}
        for field_name in field_names:
            if field_name not in existing_field_names and field_name not in system_fields:
                raise ValidationError(f"Field '{field_name}' does not exist in space")

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
                raise ValidationError(f"Field '{field_name}' does not exist in space")

            # Check if field can be hidden (must have default if required)
            if field.required and field.default is None:
                raise ValidationError(
                    f"Field '{field_name}' is required but has no default value. Cannot hide it in create form."
                )

        await self._collection.update_one({"_id": space_id}, {"$set": {"hidden_create_fields": field_names}})
        await self.update_cache(space_id)
        return self.get_space(space_id)

    async def update_note_detail_template(self, space_id: str, template: str | None) -> None:
        """Update note detail template for customizing individual note display."""
        self.get_space(space_id)  # Ensure space exists

        await self._collection.update_one({"_id": space_id}, {"$set": {"note_detail_template": template}})
        await self.update_cache(space_id)

    async def update_note_list_template(self, space_id: str, template: str | None) -> None:
        """Update note list template for customizing note list items."""
        self.get_space(space_id)  # Ensure space exists

        await self._collection.update_one({"_id": space_id}, {"$set": {"note_list_template": template}})
        await self.update_cache(space_id)

    async def add_filter(self, space_id: str, filter: Filter) -> Space:
        """Add a new filter to space."""
        space = self.get_space(space_id)

        # Validate the filter
        errors = validate_filter(space, filter)
        if errors:
            raise ValidationError("; ".join(errors))

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

    def export_as_json(self, space_id: str) -> str:
        """Export space data as JSON format."""
        space = self.get_space(space_id)
        return space_to_json(space)

    async def import_from_json(self, json_content: str, member: str) -> Space:
        """Import space from JSON format with full validation before creation."""
        existing_space_ids = self.get_space_ids()
        import_data = validate_json_import(json_content, existing_space_ids)

        await self.create_space(import_data.space_id, import_data.name, member)

        for field in import_data.fields:
            await self.add_field(import_data.space_id, field)

        if import_data.list_fields:
            await self.update_list_fields(import_data.space_id, import_data.list_fields)

        if import_data.hidden_create_fields:
            await self.update_hidden_create_fields(import_data.space_id, import_data.hidden_create_fields)

        return self.get_space(import_data.space_id)

    async def delete_space(self, space_id: str) -> None:
        """Delete a space and update cache."""
        log = logger.bind(space_id=space_id, action="delete_space")

        if not self.space_exists(space_id):
            log.warning("space_not_found")
            raise NotFoundError(f"Space '{space_id}' not found")

        await self._collection.delete_one({"_id": space_id})
        del self._spaces[space_id]
        # Note and Comment collections cleanup will be handled by the App layer

        log.debug("space_deleted")

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

    async def update_telegram_config(self, space_id: str, telegram_config: dict[str, str]) -> None:
        """Update Telegram configuration for a space."""
        log = logger.bind(space_id=space_id, action="update_telegram_config")

        if not self.space_exists(space_id):
            raise NotFoundError(f"Space '{space_id}' not found")

        # Convert form data to TelegramConfig
        config = None
        if telegram_config.get("enabled") == "on":
            config = TelegramConfig(
                enabled=True,
                bot_id=telegram_config["bot_id"],
                channel_id=telegram_config["channel_id"],
                templates=TelegramConfig.Templates(
                    new_note=telegram_config.get("template_new_note", ""),
                    field_update=telegram_config.get("template_field_update", ""),
                    comment=telegram_config.get("template_comment", ""),
                ),
            )

        await self._collection.update_one({"_id": space_id}, {"$set": {"telegram": config.model_dump() if config else None}})

        # Update cache
        self._spaces[space_id].telegram = config
        log.debug("telegram_config_updated")

    async def on_start(self) -> None:
        await self.update_cache()
        logger.debug("space_service_started", space_count=len(self._spaces))
