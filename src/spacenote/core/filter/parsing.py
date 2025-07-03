from typing import Any

from spacenote.core.field.models import FieldValueType
from spacenote.core.filter.models import Filter, FilterCondition, FilterOperator


def parse_filter_value(value_str: str) -> FieldValueType:
    """Parse string value to appropriate type."""
    value = value_str.strip()

    # Try boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # For numbers, we keep them as strings since filter values need to be FieldValueType
    # which doesn't include int/float. The actual type conversion happens during filtering.
    return value


def parse_filter_conditions(raw_data: dict[str, Any]) -> list[FilterCondition]:
    """Parse dynamic condition fields from raw form data."""
    conditions = []
    i = 0
    while f"condition_field_{i}" in raw_data:
        field = raw_data.get(f"condition_field_{i}")
        operator = raw_data.get(f"condition_operator_{i}")
        value = raw_data.get(f"condition_value_{i}")

        if field and operator and value is not None:
            try:
                # Convert to string if needed
                value_str = str(value) if not isinstance(value, str) else value
                parsed_value = parse_filter_value(value_str)
                conditions.append(FilterCondition(field=str(field), operator=FilterOperator(str(operator)), value=parsed_value))
            except (KeyError, ValueError):
                continue  # Skip invalid conditions
        i += 1

    return conditions


def parse_raw_filter_data(raw_data: dict[str, Any]) -> Filter:
    """Parse raw data (like form data) into Filter object."""
    # Parse conditions from dynamic form data
    conditions = parse_filter_conditions(raw_data)

    # Parse sort fields
    sort_str = str(raw_data.get("sort", ""))
    sort_fields = [f.strip() for f in sort_str.split(",") if f.strip()]

    # Parse list fields
    list_fields_str = str(raw_data.get("list_fields", ""))
    list_fields = [f.strip() for f in list_fields_str.split(",") if f.strip()]

    return Filter(
        id=str(raw_data.get("id", "")).strip(),
        title=str(raw_data.get("title", "")).strip(),
        description=str(raw_data.get("description", "")).strip(),
        conditions=conditions,
        sort=sort_fields,
        list_fields=list_fields,
    )
