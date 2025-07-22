from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spacenote.core.field.models import SpaceField
    from spacenote.core.space.models import Space
    from spacenote.core.user.models import User

from spacenote.core.attachment.models import AttachmentCategory
from spacenote.core.core import Service
from spacenote.core.field.models import FieldType, FieldValueType
from spacenote.core.special.models import SpecialValue


class SpecialService(Service):
    """Service for resolving special values like @me and @last."""

    async def resolve_special_value(
        self, value: str, field: "SpaceField", space: "Space", current_user: "User | None" = None
    ) -> FieldValueType:
        """Resolve a special value to its actual value.

        Args:
            value: The special value to resolve (e.g., "@me", "@last")
            field: The field definition
            space: The space containing the field
            current_user: The current user for @me resolution

        Returns:
            The resolved value
        """
        try:
            special_value = SpecialValue(value)
        except ValueError:
            # Not a special value, return as-is
            return value

        if special_value == SpecialValue.CURRENT_USER:
            return await self._resolve_current_user(field, space, current_user)
        if special_value == SpecialValue.LAST:
            return await self._resolve_last(field, space)

        # Unknown special value
        return value

    async def _resolve_current_user(self, field: "SpaceField", space: "Space", current_user: "User | None") -> FieldValueType:
        """Resolve @me special value."""
        if field.type != FieldType.USER:
            raise ValueError("Special value @me is only valid for USER fields")

        if not current_user:
            return None

        # Check if current user is a member of the space
        if current_user.id not in space.members:
            return None

        return current_user.id

    async def _resolve_last(self, field: "SpaceField", space: "Space") -> FieldValueType:
        """Resolve @last special value."""
        if field.type != FieldType.IMAGE:
            raise ValueError("Special value @last is only valid for IMAGE fields")

        # Get the last unassigned image attachment
        unassigned_attachments = await self.core.services.attachment.get_space_attachments(space.id, unassigned_only=True)

        # Filter for images only
        image_attachments = [att for att in unassigned_attachments if att.category == AttachmentCategory.IMAGES]

        if not image_attachments:
            return None

        # Return the ID of the most recent image (already sorted by _id desc)
        return image_attachments[0].id

    async def resolve_field_default(
        self, field: "SpaceField", space: "Space", current_user: "User | None" = None
    ) -> FieldValueType:
        """Resolve a field's default value, handling special values.

        Args:
            field: The field definition
            space: The space containing the field
            current_user: The current user (for @me resolution)

        Returns:
            The resolved default value
        """
        if field.default is None:
            return None

        # Check if it's a special value
        if isinstance(field.default, str) and field.default in [sv.value for sv in SpecialValue]:
            return await self.resolve_special_value(field.default, field, space, current_user)

        # Return the default as-is
        return field.default

    async def resolve_field_values(
        self, space: "Space", validated_fields: dict[str, FieldValueType], current_user: "User | None" = None
    ) -> dict[str, FieldValueType]:
        """Resolve special values in validated field values.

        Args:
            space: The space containing field definitions
            validated_fields: Field values that may contain special values
            current_user: The current user for @me resolution

        Returns:
            Field values with special values resolved
        """
        resolved_fields = {}

        for field in space.fields:
            field_name = field.name
            field_value = validated_fields.get(field_name)

            # Resolve special values in field values
            if isinstance(field_value, str) and field_value in [sv.value for sv in SpecialValue]:
                resolved_value = await self.resolve_special_value(field_value, field, space, current_user)
                resolved_fields[field_name] = resolved_value
            else:
                resolved_fields[field_name] = field_value

        return resolved_fields
