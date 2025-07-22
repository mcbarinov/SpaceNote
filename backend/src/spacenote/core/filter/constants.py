from spacenote.core.field.models import FieldType
from spacenote.core.filter.models import FilterOperator

# Mapping of field types to their valid operators
FIELD_TYPE_OPERATORS = {
    FieldType.STRING: {
        FilterOperator.EQ,
        FilterOperator.NE,
        FilterOperator.CONTAINS,
        FilterOperator.STARTSWITH,
        FilterOperator.ENDSWITH,
        FilterOperator.IN,
    },
    FieldType.MARKDOWN: {
        FilterOperator.EQ,
        FilterOperator.NE,
        FilterOperator.CONTAINS,
        FilterOperator.STARTSWITH,
        FilterOperator.ENDSWITH,
        FilterOperator.IN,
    },
    FieldType.BOOLEAN: {FilterOperator.EQ, FilterOperator.NE},
    FieldType.CHOICE: {FilterOperator.EQ, FilterOperator.NE, FilterOperator.IN},
    FieldType.TAGS: {FilterOperator.CONTAINS, FilterOperator.IN, FilterOperator.ALL},
    FieldType.USER: {FilterOperator.EQ, FilterOperator.NE, FilterOperator.IN},
    FieldType.DATETIME: {
        FilterOperator.EQ,
        FilterOperator.NE,
        FilterOperator.GT,
        FilterOperator.GTE,
        FilterOperator.LT,
        FilterOperator.LTE,
    },
    FieldType.INT: {
        FilterOperator.EQ,
        FilterOperator.NE,
        FilterOperator.GT,
        FilterOperator.GTE,
        FilterOperator.LT,
        FilterOperator.LTE,
        FilterOperator.IN,
    },
    FieldType.FLOAT: {
        FilterOperator.EQ,
        FilterOperator.NE,
        FilterOperator.GT,
        FilterOperator.GTE,
        FilterOperator.LT,
        FilterOperator.LTE,
        FilterOperator.IN,
    },
}

# Built-in field types mapping
BUILTIN_FIELD_OPERATORS = {
    "id": FIELD_TYPE_OPERATORS[FieldType.INT],
    "author": FIELD_TYPE_OPERATORS[FieldType.USER],
    "created_at": FIELD_TYPE_OPERATORS[FieldType.DATETIME],
}


def get_valid_operators_for_field_type(field_type: str) -> set[FilterOperator]:
    """Get set of valid operators for a given field type."""
    # Check built-in fields first
    if field_type in BUILTIN_FIELD_OPERATORS:
        return BUILTIN_FIELD_OPERATORS[field_type]

    # Check custom field types
    try:
        field_enum = FieldType(field_type)
        return FIELD_TYPE_OPERATORS[field_enum]
    except ValueError:
        return set()  # Return empty set for unknown types


def get_valid_operators_list_for_field_type(field_type: str) -> list[FilterOperator]:
    """Get list of valid operators for a given field type (for API usage)."""
    return list(get_valid_operators_for_field_type(field_type))
