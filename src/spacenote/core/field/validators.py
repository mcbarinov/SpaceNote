import re

from spacenote.core.field.models import FieldOption, FieldType, SpaceField
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
