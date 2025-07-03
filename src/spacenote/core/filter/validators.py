from spacenote.core.filter.constants import get_valid_operators_for_field_type
from spacenote.core.filter.models import Filter, FilterCondition, FilterOperator
from spacenote.core.space.models import Space


def validate_filter(space: Space, filter: Filter) -> list[str]:
    """Validate filter against space fields. Returns list of errors."""
    errors = []

    # Check filter ID uniqueness within space
    if any(f.id == filter.id and f is not filter for f in space.filters):
        errors.append(f"Filter ID '{filter.id}' already exists in space")

    # Validate conditions
    for condition in filter.conditions:
        field_errors = _validate_condition(space, condition)
        errors.extend(field_errors)

    # Validate sort fields
    for sort_field in filter.sort:
        field_name = sort_field.lstrip("-")  # Remove DESC prefix
        if not _field_exists(space, field_name):
            errors.append(f"Sort field '{field_name}' does not exist in space")

    # Validate list_fields
    errors.extend(
        f"List field '{field_name}' does not exist in space"
        for field_name in filter.list_fields
        if not _field_exists(space, field_name)
    )

    return errors


def _validate_condition(space: Space, condition: FilterCondition) -> list[str]:
    """Validate a single filter condition."""
    errors = []

    # Check if field exists
    if not _field_exists(space, condition.field):
        errors.append(f"Field '{condition.field}' does not exist in space")
        return errors

    field = space.get_field(condition.field)
    if not field:
        return errors

    # Validate operator compatibility with field type
    operator_errors = _validate_operator_for_field_type(field.type, condition.operator)
    errors.extend(operator_errors)

    return errors


def _field_exists(space: Space, field_name: str) -> bool:
    """Check if field exists in space (including built-in fields)."""
    # Built-in fields
    if field_name in ["id", "author", "created_at"]:
        return True

    # Custom fields
    return space.get_field(field_name) is not None


def _validate_operator_for_field_type(field_type: str, operator: FilterOperator) -> list[str]:
    """Validate operator compatibility with field type."""
    allowed = get_valid_operators_for_field_type(field_type)

    if not allowed:
        return [f"Unknown field type: {field_type}"]

    if operator not in allowed:
        return [f"Operator '{operator.value}' is not valid for field type '{field_type}'"]

    return []
