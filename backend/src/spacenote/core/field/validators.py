import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from spacenote.core.errors import ValidationError
from spacenote.core.field.models import FieldOption, FieldType, FieldValueType, SpaceField
from spacenote.core.space.models import Space
from spacenote.core.special.models import SpecialValue


class FieldValidator(ABC):
    """Base class for field validators."""

    @abstractmethod
    def validate_configuration(self, field: SpaceField) -> None:
        """Validate field configuration (options and default values)."""
        ...

    @abstractmethod
    def validate_value(self, field: SpaceField, raw_value: str, context: dict[str, Any] | None = None) -> FieldValueType:
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
        raise ValidationError(f"No validator registered for field type: {field_type}")
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
            raise ValidationError("STRING field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        return raw_value.strip() if raw_value else None


@register_validator(FieldType.MARKDOWN)
class MarkdownValidator(FieldValidator):
    """Validator for MARKDOWN fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        # Markdown fields don't have special configuration requirements
        if field.default is not None and not isinstance(field.default, str):
            raise ValidationError("MARKDOWN field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        return raw_value.strip() if raw_value else None


@register_validator(FieldType.BOOLEAN)
class BooleanValidator(FieldValidator):
    """Validator for BOOLEAN fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, bool):
            raise ValidationError("BOOLEAN field default must be a boolean value")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        # HTML forms should send "true" or "false" explicitly
        if raw_value == "true":
            return True
        if raw_value == "false":
            return False
        raise ValidationError(f"Invalid boolean value '{raw_value}'. Expected 'true' or 'false'")


@register_validator(FieldType.CHOICE)
class ChoiceValidator(FieldValidator):
    """Validator for CHOICE fields. CHOICE fields work strictly with string values only."""

    def validate_configuration(self, field: SpaceField) -> None:
        values = field.options.get(FieldOption.VALUES, [])
        if not values or not isinstance(values, list):
            raise ValidationError("CHOICE field must have at least one value option")

        # Check for duplicates while preserving order
        if len(set(values)) != len(values):
            raise ValidationError("Duplicate value in CHOICE field options")

        # Check that values don't contain only whitespace
        for value in values:
            if not value.strip():
                raise ValidationError("CHOICE field values cannot be empty or contain only whitespace")

        # Check that default is among available values
        if field.default and field.default not in values:
            raise ValidationError(f"Default value '{field.default}' must be one of the available choices")

    def validate_value(self, field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        # Validate that the choice is in available options
        available_choices = field.options.get(FieldOption.VALUES, [])
        if isinstance(available_choices, list) and raw_value not in available_choices:
            raise ValidationError(f"Invalid choice '{raw_value}' for field '{field.name}'")
        return raw_value


@register_validator(FieldType.TAGS)
class TagsValidator(FieldValidator):
    """Validator for TAGS fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, list):
            raise ValidationError("TAGS field default must be a list of strings")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        # Parse comma-separated tags
        tags = [tag.strip() for tag in raw_value.split(",") if tag.strip()]
        return tags if tags else None


@register_validator(FieldType.USER)
class UserValidator(FieldValidator):
    """Validator for USER fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and field.default not in [SpecialValue.CURRENT_USER] and not isinstance(field.default, str):
            raise ValidationError("USER field default must be a string (user ID) or @me")

    def validate_value(self, _field: SpaceField, raw_value: str, context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        # Check that context with members is provided
        if not context or "members" not in context:
            raise ValidationError("UserValidator requires 'members' in context")

        # Validate that the user is a member of the space
        members = context["members"]
        if raw_value not in members:
            raise ValidationError(f"User '{raw_value}' is not a member of this space")
        return raw_value


@register_validator(FieldType.DATETIME)
class DateTimeValidator(FieldValidator):
    """Validator for DATETIME fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and not isinstance(field.default, str):
            raise ValidationError("DATETIME field default must be a string")

    def validate_value(self, _field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        return raw_value.strip() if raw_value else None


@register_validator(FieldType.INT)
class IntValidator(FieldValidator):
    """Validator for INT fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        # Convert string default to int if needed (from web forms)
        if field.default is not None:
            if isinstance(field.default, str):
                try:
                    field.default = int(field.default)
                except ValueError:
                    raise ValidationError(f"INT field default '{field.default}' must be a valid integer") from None
            elif not isinstance(field.default, int):
                raise ValidationError("INT field default must be an integer")

        # Validate min/max constraints
        min_val = field.options.get(FieldOption.MIN)
        max_val = field.options.get(FieldOption.MAX)

        if (
            min_val is not None
            and isinstance(min_val, int)
            and max_val is not None
            and isinstance(max_val, int)
            and min_val > max_val
        ):
            raise ValidationError("INT field min value cannot be greater than max value")

    def validate_value(self, field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        try:
            value = int(raw_value)
        except ValueError:
            raise ValidationError(f"Invalid integer value '{raw_value}' for field '{field.name}'") from None

        # Check min/max constraints
        min_val = field.options.get(FieldOption.MIN)
        max_val = field.options.get(FieldOption.MAX)

        if min_val is not None and isinstance(min_val, int) and value < min_val:
            raise ValidationError(f"Value {value} is below minimum {min_val} for field '{field.name}'")
        if max_val is not None and isinstance(max_val, int) and value > max_val:
            raise ValidationError(f"Value {value} is above maximum {max_val} for field '{field.name}'")

        return value


@register_validator(FieldType.FLOAT)
class FloatValidator(FieldValidator):
    """Validator for FLOAT fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        # Convert string default to float if needed (from web forms)
        if field.default is not None:
            if isinstance(field.default, str):
                try:
                    field.default = float(field.default)
                except ValueError:
                    raise ValidationError(f"FLOAT field default '{field.default}' must be a valid number") from None
            elif not isinstance(field.default, (int, float)):
                raise ValidationError("FLOAT field default must be a number")

        # Validate min/max constraints
        min_val = field.options.get(FieldOption.MIN)
        max_val = field.options.get(FieldOption.MAX)

        if (
            min_val is not None
            and isinstance(min_val, (int, float))
            and max_val is not None
            and isinstance(max_val, (int, float))
            and min_val > max_val
        ):
            raise ValidationError("FLOAT field min value cannot be greater than max value")

    def validate_value(self, field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        try:
            value = float(raw_value)
        except ValueError:
            raise ValidationError(f"Invalid float value '{raw_value}' for field '{field.name}'") from None

        # Check min/max constraints
        min_val = field.options.get(FieldOption.MIN)
        max_val = field.options.get(FieldOption.MAX)

        if min_val is not None and isinstance(min_val, (int, float)) and value < min_val:
            raise ValidationError(f"Value {value} is below minimum {min_val} for field '{field.name}'")
        if max_val is not None and isinstance(max_val, (int, float)) and value > max_val:
            raise ValidationError(f"Value {value} is above maximum {max_val} for field '{field.name}'")

        return value


@register_validator(FieldType.IMAGE)
class ImageValidator(FieldValidator):
    """Validator for IMAGE fields."""

    def validate_configuration(self, field: SpaceField) -> None:
        if field.default is not None and field.default not in [SpecialValue.LAST] and not isinstance(field.default, int):
            raise ValidationError("IMAGE field default must be an integer (attachment_id) or @last")

    def validate_value(self, field: SpaceField, raw_value: str, _context: dict[str, Any] | None = None) -> FieldValueType:
        if not raw_value:
            return None

        try:
            attachment_id = int(raw_value)
        except ValueError:
            raise ValidationError(f"Invalid attachment ID '{raw_value}' for field '{field.name}'") from None

        return attachment_id


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
        raise ValidationError(f"Invalid field name '{new_field.name}'. Must be lowercase, no spaces, and start with a letter.")

    # Check for duplicate field names
    existing_names = {f.name for f in space.fields}
    if new_field.name in existing_names:
        raise ValidationError(f"Field name '{new_field.name}' already exists in space '{space.id}'")

    # Validate field configuration (options and default values)
    validate_field_configuration(new_field)

    return new_field


def validate_field_configuration(field: SpaceField) -> None:
    """Validate field options and default values based on field type."""
    get_validator(field.type).validate_configuration(field)


async def validate_note_fields(
    space: Space,
    field_values: dict[str, str],
    skip_missing: bool = False,
) -> dict[str, FieldValueType]:
    """Validate and convert field values for a note based on space field definitions.

    Args:
        space: The space containing field definitions
        field_values: Raw field values from the form
        skip_missing: If True, missing fields will use their default values (for hidden fields)
    """

    validated_fields: dict[str, FieldValueType] = {}

    # Prepare validation context
    validation_context: dict[str, Any] = {
        "members": space.members,
        "space_id": space.id,
    }

    for field in space.fields:
        field_name = field.name

        # Handle missing fields, it's about Space.hidden_create_fields
        if field_name not in field_values:
            if skip_missing:
                # Use default value for missing fields, or None
                if field.default is not None:
                    validated_fields[field_name] = field.default
                elif field.required:
                    raise ValidationError(f"Field '{field_name}' is required but has no default value")
                else:
                    # Optional field without default - store as None
                    validated_fields[field_name] = None
                continue
            raise ValidationError(f"Missing field '{field_name}' in form data")

        raw_value = field_values[field_name]

        # Get the appropriate validator and validate the value
        validator = get_validator(field.type)
        validated_value = validator.validate_value(field, raw_value, validation_context)

        # Handle required fields AFTER validation
        if field.required and validated_value is None:
            raise ValidationError(f"Field '{field_name}' is required")

        # Always include the field, even if it's None
        validated_fields[field_name] = validated_value

    return validated_fields
