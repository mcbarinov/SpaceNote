from typing import Any

from spacenote.core.field.models import FieldValueType
from spacenote.core.filter.models import Filter, FilterCondition, FilterOperator
from spacenote.core.space.models import Space
from spacenote.core.special.filters import resolve_special_values
from spacenote.core.user.models import User


def build_mongodb_query(filter: Filter, space: Space, current_user: User | None = None) -> dict[str, FieldValueType]:
    """Build MongoDB query from filter conditions."""
    # Resolve special values first
    resolved_filter = resolve_special_values(filter, space, current_user)
    query: dict[str, Any] = {}
    for condition in resolved_filter.conditions:
        field_query = _build_field_query(condition)

        # Map field name to MongoDB path
        field_path = condition.field
        if field_path == "id":
            field_path = "_id"
        elif field_path not in ["author", "created_at"]:
            # Custom fields are stored in 'fields' subdocument
            field_path = f"fields.{condition.field}"

        # Combine multiple conditions with AND logic
        if field_path in query:
            # If multiple conditions on same field, combine with $and
            if "$and" not in query:
                existing_query = query.copy()
                query = {"$and": [existing_query]}
            query["$and"].append({field_path: field_query})
        else:
            query[field_path] = field_query
    return query


def _build_field_query(condition: FilterCondition) -> Any:  # noqa: ANN401
    """Build MongoDB query for a single field condition."""
    operator = condition.operator
    value = condition.value

    match operator:
        case FilterOperator.EQ:
            return value  # MongoDB treats direct value as equality
        case FilterOperator.NE:
            return {"$ne": value}
        case FilterOperator.GT:
            return {"$gt": value}
        case FilterOperator.GTE:
            return {"$gte": value}
        case FilterOperator.LT:
            return {"$lt": value}
        case FilterOperator.LTE:
            return {"$lte": value}
        case FilterOperator.CONTAINS:
            return {"$regex": str(value), "$options": "i"}
        case FilterOperator.STARTSWITH:
            return {"$regex": f"^{value!s}", "$options": "i"}
        case FilterOperator.ENDSWITH:
            return {"$regex": f"{value!s}$", "$options": "i"}
        case FilterOperator.IN:
            if isinstance(value, list):
                return {"$in": value}
            # For TAGS field - check if any tag matches
            return {"$in": [value]}
        case FilterOperator.ALL:
            if isinstance(value, list):
                return {"$all": value}
            return {"$all": [value]}
        case _:
            raise ValueError(f"Unsupported operator: {operator}")


def build_sort_spec(filter: Filter) -> list[tuple[str, int]]:
    """Build MongoDB sort specification from filter sort fields."""
    sort_spec = []

    for sort_field in filter.sort:
        if sort_field.startswith("-"):  # Descending order
            field_name = sort_field[1:]
            direction = -1
        else:  # Ascending order
            field_name = sort_field
            direction = 1

        # MongoDB field mapping
        if field_name == "id":
            field_name = "_id"
        elif field_name not in ["author", "created_at"]:
            field_name = f"fields.{field_name}"  # Custom fields are stored in 'fields' subdocument

        sort_spec.append((field_name, direction))

    return sort_spec


def get_display_fields(space: Space, filter_obj: Filter | None = None) -> list[str]:
    """Get fields to display in notes list."""
    # Always show built-in fields
    display_fields = ["id", "author", "created_at"]

    if filter_obj and filter_obj.list_fields:
        # Add filter-specific fields
        display_fields.extend(filter_obj.list_fields)
    else:
        # Add space default fields
        display_fields.extend(space.list_fields)

    # Remove duplicates while preserving order
    seen = set()
    result = []
    for field in display_fields:
        if field not in seen:
            seen.add(field)
            result.append(field)

    return result
