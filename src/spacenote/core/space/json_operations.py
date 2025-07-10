import json
from dataclasses import dataclass
from typing import Any

from spacenote.core.field.models import FieldType, SpaceField
from spacenote.core.field.validators import validate_new_field
from spacenote.core.space.models import Space


@dataclass
class ImportData:
    """Data structure for validated JSON import data."""

    space_id: str
    name: str
    fields: list[SpaceField]
    list_fields: list[str]
    hidden_create_fields: list[str]


def space_to_json(space: Space) -> str:
    """Export space data as JSON format."""
    space_dict = _space_to_dict(space)
    return json.dumps(space_dict, indent=2, ensure_ascii=False)


def _space_to_dict(space: Space) -> dict[str, Any]:
    """Convert space to dict for JSON serialization."""
    space_dict: dict[str, Any] = {
        "version": "1.0",
        "id": space.id,
        "name": space.name,
        "members": space.members,
        "list_fields": space.list_fields,
        "hidden_create_fields": space.hidden_create_fields,
        "fields": [],
    }

    # Convert fields to dict format
    for field in space.fields:
        field_dict = {
            "name": field.name,
            "type": field.type.value,
            "required": field.required,
            "options": field.options,
            "default": field.default,
        }
        space_dict["fields"].append(field_dict)

    return space_dict


def validate_json_import(json_content: str, existing_space_ids: list[str]) -> ImportData:
    """Validate JSON import data and return structured ImportData."""
    # Phase 1: Parse JSON
    try:
        space_data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e

    if not isinstance(space_data, dict):
        raise TypeError("JSON content must be a dictionary")

    # Phase 2: Validate version (optional but recommended)
    if "version" in space_data:
        version = space_data["version"]
        if version != "1.0":
            raise ValueError(f"Unsupported import format version: {version}")

    # Phase 3: Validate space data
    space_id, name = _validate_space_data(space_data, existing_space_ids)

    # Phase 4: Validate fields data
    validated_fields = _validate_fields_data(space_data)

    # Phase 5: Validate list_fields data
    field_names = {field.name for field in validated_fields}
    list_fields = _validate_list_fields_data(space_data, field_names)

    # Phase 6: Validate hidden_create_fields data
    hidden_create_fields = _validate_hidden_create_fields_data(space_data, field_names)

    # Phase 7: Validate field configurations using existing validators
    temp_space = Space(id=space_id, name=name, members=[], fields=[], list_fields=[])
    for field in validated_fields:
        validate_new_field(temp_space, field)
        temp_space.fields.append(field)

    # Phase 8: Validate that hidden fields can be hidden (have defaults if required)
    for hidden_field_name in hidden_create_fields:
        hidden_field: SpaceField | None = None
        for f in validated_fields:
            if f.name == hidden_field_name:
                hidden_field = f
                break
        if hidden_field and hidden_field.required and hidden_field.default is None:
            raise ValueError(f"Field '{hidden_field_name}' is required but has no default value. Cannot hide it in create form.")

    return ImportData(
        space_id=space_id,
        name=name,
        fields=validated_fields,
        list_fields=list_fields,
        hidden_create_fields=hidden_create_fields,
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


def _validate_hidden_create_fields_data(space_data: dict[str, Any], field_names: set[str]) -> list[str]:
    """Validate hidden_create_fields data."""
    if "hidden_create_fields" not in space_data:
        return []

    if not isinstance(space_data["hidden_create_fields"], list):
        raise TypeError("hidden_create_fields must be a list")

    hidden_create_fields = space_data["hidden_create_fields"]
    # Validate that all hidden_create_fields reference existing fields
    for hidden_field in hidden_create_fields:
        if not isinstance(hidden_field, str):
            raise TypeError(f"hidden_create_fields entry must be a string, got {type(hidden_field)}")
        if hidden_field not in field_names:
            raise ValueError(f"hidden_create_fields references non-existent field: '{hidden_field}'")

    return hidden_create_fields
