from typing import TYPE_CHECKING, Any

from spacenote.core.export.models import ExportData
from spacenote.core.field.validators import validate_field_configuration

if TYPE_CHECKING:
    from spacenote.core.space.service import SpaceService


def is_valid_space_id(space_id: str) -> bool:
    """Check if space ID is valid slug format."""
    return bool(space_id and space_id.replace("-", "").replace("_", "").isalnum())


async def validate_import_data(data: dict[str, Any], space_service: "SpaceService") -> list[str]:
    """Validate import data structure and content."""
    errors = []

    # 1. Check version
    if data.get("version") != "1.0":
        errors.append(f"Unsupported version: {data.get('version')}")
        return errors

    # 2. Validate structure
    try:
        export_data = ExportData(**data)
    except Exception as e:
        errors.append(f"Invalid data structure: {e!s}")
        return errors

    # 3. Validate space ID
    if not is_valid_space_id(export_data.space.id):
        errors.append(f"Invalid space ID format: {export_data.space.id}")

    # 4. Check if space already exists
    if space_service.space_exists(export_data.space.id):
        errors.append(f"Space '{export_data.space.id}' already exists")

    # 5. Validate fields
    if not export_data.space.fields:
        errors.append("Space must have at least one field")

    field_names = set()
    for field in export_data.space.fields:
        if field.name in field_names:
            errors.append(f"Duplicate field name: {field.name}")
        field_names.add(field.name)

        # Validate field configuration
        try:
            validate_field_configuration(field)
        except Exception as e:
            errors.append(f"Field '{field.name}': {e!s}")

    # 6. Validate list_fields reference existing fields
    for col in export_data.space.list_fields:
        if col not in field_names:
            errors.append(f"List field '{col}' references non-existent field")  # noqa: PERF401

    # 7. Validate filters reference existing fields
    for filter_obj in export_data.space.filters:
        if filter_obj.list_fields:
            for field_name in filter_obj.list_fields:
                if field_name not in field_names:
                    errors.append(f"Filter list field '{field_name}' references non-existent field")  # noqa: PERF401

    # 8. If notes are included, validate them
    if export_data.notes:
        for note in export_data.notes:
            # Check that all note fields are defined in space
            for field_name in note.fields:
                if field_name not in field_names:
                    errors.append(f"Note {note.id} has unknown field: {field_name}")  # noqa: PERF401

    # 9. If comments are included, validate note references
    if export_data.comments:
        note_ids = {note.id for note in export_data.notes}
        for comment in export_data.comments:
            if comment.note_id not in note_ids:
                errors.append(f"Comment {comment.id} references non-existent note: {comment.note_id}")  # noqa: PERF401

    return errors
