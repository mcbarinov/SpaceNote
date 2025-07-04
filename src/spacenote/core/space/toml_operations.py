import tomllib
from dataclasses import dataclass
from typing import Any

import tomli_w

from spacenote.core.field.models import FieldOption, FieldOptionValueType, FieldType, FieldValueType, SpaceField
from spacenote.core.field.validators import validate_new_field
from spacenote.core.space.models import Space


@dataclass
class ImportData:
    """Data structure for validated TOML import data."""

    space_id: str
    name: str
    fields: list[SpaceField]
    list_fields: list[str]


def space_to_toml(space: Space) -> str:
    """Export space data as TOML format."""
    space_dict = _space_to_dict(space)
    return tomli_w.dumps(space_dict)


def _space_to_dict(space: Space) -> dict[str, Any]:
    """Convert space to dict for TOML serialization."""
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

    return space_dict


def validate_toml_import(toml_content: str, existing_space_ids: list[str]) -> ImportData:
    """Validate TOML import data and return structured ImportData."""
    # Phase 1: Parse TOML
    try:
        space_data = tomllib.loads(toml_content)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML format: {e}") from e

    if not isinstance(space_data, dict):
        raise TypeError("TOML content must be a dictionary")

    # Phase 2: Validate space data
    space_id, name = _validate_space_data(space_data, existing_space_ids)

    # Phase 3: Validate fields data
    validated_fields = _validate_fields_data(space_data)

    # Phase 4: Validate list_fields data
    field_names = {field.name for field in validated_fields}
    list_fields = _validate_list_fields_data(space_data, field_names)

    # Phase 5: Validate field configurations using existing validators
    temp_space = Space(id=space_id, name=name, members=[], fields=[], list_fields=[])
    for field in validated_fields:
        validate_new_field(temp_space, field)
        temp_space.fields.append(field)

    return ImportData(
        space_id=space_id,
        name=name,
        fields=validated_fields,
        list_fields=list_fields,
    )


def _validate_space_data(space_data: dict[str, Any], existing_space_ids: list[str]) -> tuple[str, str]:
    """Validate basic space data and return space_id and name."""
    # Validate required space fields
    if "id" not in space_data:
        raise ValueError("Missing required field: id")
    if "name" not in space_data:
        raise ValueError("Missing required field: name")

    space_id = space_data["id"]
    name = space_data["name"]

    # Validate space ID format (same validation as create_space)
    if not space_id or not space_id.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Space ID must be a valid slug (alphanumeric with hyphens/underscores)")

    # Check if space already exists
    if space_id in existing_space_ids:
        raise ValueError(f"Space with ID '{space_id}' already exists")

    # Validate name is not empty
    if not name or not name.strip():
        raise ValueError("Space name cannot be empty")

    return space_id, name


def _validate_fields_data(space_data: dict[str, Any]) -> list[SpaceField]:
    """Validate and prepare fields data."""
    validated_fields: list[SpaceField] = []
    if "fields" not in space_data:
        return validated_fields

    if not isinstance(space_data["fields"], list):
        raise TypeError("Fields must be a list")

    field_names_seen = set()
    for i, field_data in enumerate(space_data["fields"]):
        # Validate field structure
        if not isinstance(field_data, dict):
            raise TypeError(f"Field {i} must be a dictionary")
        if "name" not in field_data or "type" not in field_data:
            raise ValueError(f"Field {i} must have 'name' and 'type'")

        field_name = field_data["name"]
        field_type_str = field_data["type"]

        # Check for duplicate field names
        if field_name in field_names_seen:
            raise ValueError(f"Duplicate field name: '{field_name}'")
        field_names_seen.add(field_name)

        # Validate field type
        try:
            field_type = FieldType(field_type_str)
        except ValueError as e:
            raise ValueError(f"Invalid field type '{field_type_str}' for field '{field_name}'") from e

        # Create and validate SpaceField object
        try:
            field = SpaceField(
                name=field_name,
                type=field_type,
                required=field_data.get("required", False),
                options=field_data.get("options", {}),
                default=field_data.get("default"),
            )
            validated_fields.append(field)
        except Exception as e:
            raise ValueError(f"Invalid field '{field_name}': {e}") from e

    return validated_fields


def _validate_list_fields_data(space_data: dict[str, Any], field_names: set[str]) -> list[str]:
    """Validate list_fields data."""
    if "list_fields" not in space_data:
        return []

    if not isinstance(space_data["list_fields"], list):
        raise TypeError("list_fields must be a list")

    list_fields = space_data["list_fields"]
    # Validate that all list_fields reference existing fields
    for list_field in list_fields:
        if not isinstance(list_field, str):
            raise TypeError(f"list_fields entry must be a string, got {type(list_field)}")
        if list_field not in field_names:
            raise ValueError(f"list_fields references non-existent field: '{list_field}'")

    return list_fields
