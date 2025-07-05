import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from spacenote.core.field.models import FieldOption, FieldType, FieldValue, SpaceField
from spacenote.core.space.models import Space


class FieldValidator(ABC):
    """Base class for field validators."""

    @abstractmethod
    def validate_configuration(self, field: SpaceField) -> None:
        """Validate field configuration (options and default values)."""
        ...

    @abstractmethod
    def validate_value(self, field: SpaceField, raw_value: str, context: dict[str, Any] | None = None) -> FieldValue:
        """Validate and convert a raw value to the appropriate type.

        Args:
            field: The field definition
            raw_value: The raw string value to validate
            context: Optional context dictionary for validation (e.g., {"members": [...]} for USER fields)
        """
        ...


# Registry to store validators by field type
VALIDATORS: dict[FieldType, FieldValidator] = {}


def register_validator(field_type: FieldType) -> Callable[[type[FieldValidator]], type[FieldValidator]]:
    """Decorator to register a validator for a specific field type."""

    def decorator(cls: type[FieldValidator]) -> type[FieldValidator]:
        VALIDATORS[field_type] = cls()
        return cls

    return decorator


def get_validator(field_type: FieldType) -> FieldValidator:
    """Get the validator for a specific field type."""
    if field_type not in VALIDATORS:
        raise ValueError(f"No validator registered for field type: {field_type}")
    return VALIDATORS[field_type]


def ensure_all_validators_registered() -> None:
    """Ensure all field types have registered validators."""
    missing_types = [field_type for field_type in FieldType if field_type not in VALIDATORS]

    if missing_types:
        raise RuntimeError(f"Missing validators for field types: {missing_types}")


@register_validator(FieldType.STRING)
class StringValidator(FieldValidator):
    """Validator for STRING fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        # String fields don't have special configuration requirements
        if field.default is not None and not isinstance(field.default, str):
            raise ValueError("STRING field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        return raw_value.strip() if raw_value else None


@register_validator(FieldType.MARKDOWN)
class MarkdownValidator(FieldValidator):
    """Validator for MARKDOWN fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        # Markdown fields don't have special configuration requirements
        if field.default is not None and not isinstance(field.default, str):
            raise ValueError("MARKDOWN field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        return raw_value.strip() if raw_value else None


@register_validator(FieldType.BOOLEAN)
class BooleanValidator(FieldValidator):
    """Validator for BOOLEAN fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, bool):
            raise ValueError("BOOLEAN field default must be a boolean value")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        # HTML forms should send "true" or "false" explicitly
        if raw_value == "true":
            return True
        if raw_value == "false":
            return False
        raise ValueError(f"Invalid boolean value '{raw_value}'. Expected 'true' or 'false'")


@register_validator(FieldType.CHOICE)
class ChoiceValidator(FieldValidator):
    """Validator for CHOICE fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        values = field.options.get(FieldOption.VALUES, [])
        if not values:
            raise ValueError("CHOICE field must have at least one value option")

        # Check for duplicates while preserving order
        if len(set(values)) != len(values):
            raise ValueError("Duplicate value in CHOICE field options")

        # Check that values don't contain only whitespace
        for value in values:
            if not value.strip():
                raise ValueError("CHOICE field values cannot be empty or contain only whitespace")

        # Check that default is among available values
        if field.default and field.default not in values:
            raise ValueError(f"Default value '{field.default}' must be one of the available choices")

    def validate_value(self, field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        if not raw_value:
            return None

        # Validate that the choice is in available options
        available_choices = field.options.get(FieldOption.VALUES, [])
        if raw_value not in available_choices:
            raise ValueError(f"Invalid choice '{raw_value}' for field '{field.name}'")
        return raw_value


@register_validator(FieldType.TAGS)
class TagsValidator(FieldValidator):
    """Validator for TAGS fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, list):
            raise ValueError("TAGS field default must be a list of strings")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        if not raw_value:
            return None

        # Parse comma-separated tags
        tags = [tag.strip() for tag in raw_value.split(",") if tag.strip()]
        return tags if tags else None


@register_validator(FieldType.USER)
class UserValidator(FieldValidator):
    """Validator for USER fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, str):
            raise ValueError("USER field default must be a string (user ID)")

    def validate_value(self, _field: SpaceField, raw_value: str, context: dict[str, Any] | None = None) -> FieldValue:
        if not raw_value:
            return None

        # Check that context with members is provided
        if not context or "members" not in context:
            raise ValueError("UserValidator requires 'members' in context")

        # Validate that the user is a member of the space
        members = context["members"]
        if raw_value not in members:
            raise ValueError(f"User '{raw_value}' is not a member of this space")
        return raw_value


@register_validator(FieldType.DATETIME)
class DateTimeValidator(FieldValidator):
    """Validator for DATETIME fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, str):
            raise ValueError("DATETIME field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValue:
        return raw_value.strip() if raw_value else None


# Ensure all field types have validators at import time
ensure_all_validators_registered()


def is_valid_field_name(s: str) -> bool:
    """
    Checks that the string:
    - contains no spaces
    - is all lowercase
    - contains only English letters, digits, and underscores
    - starts with a letter
    """
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", s))


def validate_new_field(space: Space, new_field: SpaceField) -> SpaceField:
    """Validate a new field being added to a space."""
    if not is_valid_field_name(new_field.name):
        raise ValueError(f"Invalid field name '{new_field.name}'. Must be lowercase, no spaces, and start with a letter.")

    # Check for duplicate field names
    existing_names = {f.name for f in space.fields}
    if new_field.name in existing_names:
        raise ValueError(f"Field name '{new_field.name}' already exists in space '{space.id}'")

    # Validate field configuration (options and default values)
    validate_field_configuration(new_field)

    return new_field


def validate_field_configuration(field: SpaceField) -> None:
    """Validate field options and default values based on field type."""
    get_validator(field.type).validate_configuration(field)


def validate_note_fields(space: Space, field_values: dict[str, str]) -> dict[str, FieldValue]:
    """Validate and convert field values for a note based on space field definitions."""

    validated_fields: dict[str, FieldValue] = {}

    # Prepare validation context
    validation_context = {
        "members": space.members,
        "space_id": space.id,
    }

    for field in space.fields:
        field_name = field.name

        # Check that field is present in field_values
        if field_name not in field_values:
            raise ValueError(f"Missing field '{field_name}' in form data")

        raw_value = field_values[field_name]

        # Get the appropriate validator and validate the value
        validator = get_validator(field.type)
        validated_value = validator.validate_value(field, raw_value, validation_context)

        # Handle required fields AFTER validation
        if field.required and validated_value is None:
            raise ValueError(f"Field '{field_name}' is required")

        # Only include non-None values
        if validated_value is not None:
            validated_fields[field_name] = validated_value

    return validated_fields
