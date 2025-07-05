import re

from spacenote.core.field.models import FieldOption, FieldType, FieldValue, SpaceField
from spacenote.core.space.models import Space


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

    # CHOICE requires values to be present
    if field.type == FieldType.CHOICE:
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

    # BOOLEAN - default must be bool
    elif field.type == FieldType.BOOLEAN:
        if field.default is not None and not isinstance(field.default, bool):
            raise ValueError("BOOLEAN field default must be a boolean value")

    # TAGS - default must be a list
    elif field.type == FieldType.TAGS:
        if field.default is not None and not isinstance(field.default, list):
            raise ValueError("TAGS field default must be a list of strings")


def validate_note_fields(space: Space, field_values: dict[str, str]) -> dict[str, FieldValue]:
    """Validate and convert field values for a note based on space field definitions."""

    validated_fields: dict[str, FieldValue] = {}

    for field in space.fields:
        field_name = field.name
        raw_value = field_values.get(field_name, "")

        # Handle required fields
        if field.required and not raw_value:
            raise ValueError(f"Field '{field_name}' is required")

        # Convert and validate based on field type
        validated_value: FieldValue = None

        if field.type in {FieldType.STRING, FieldType.MARKDOWN}:
            validated_value = raw_value.strip() if raw_value else None

        elif field.type == FieldType.BOOLEAN:
            # HTML checkbox sends "true" or nothing
            validated_value = raw_value == "true"

        elif field.type == FieldType.CHOICE:
            if raw_value:
                # Validate that the choice is in available options
                available_choices = field.options.get(FieldOption.VALUES, [])
                if raw_value not in available_choices:
                    raise ValueError(f"Invalid choice '{raw_value}' for field '{field_name}'")
                validated_value = raw_value
            else:
                validated_value = None

        elif field.type == FieldType.TAGS:
            if raw_value:
                # Parse comma-separated tags
                tags = [tag.strip() for tag in raw_value.split(",") if tag.strip()]
                validated_value = tags if tags else None
            else:
                validated_value = None

        elif field.type == FieldType.USER:
            if raw_value:
                # Validate that the user is a member of the space
                if raw_value not in space.members:
                    raise ValueError(f"User '{raw_value}' is not a member of space '{space.id}'")
                validated_value = raw_value
            else:
                validated_value = None

        elif field.type == FieldType.DATETIME:
            validated_value = raw_value.strip() if raw_value else None

        # Only include non-None values
        if validated_value is not None:
            validated_fields[field_name] = validated_value

    return validated_fields
