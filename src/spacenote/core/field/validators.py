import re

from spacenote.core.field.models import SpaceField
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

    return new_field
