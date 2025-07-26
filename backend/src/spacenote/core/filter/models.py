from enum import StrEnum

from pydantic import BaseModel

from spacenote.core.field.models import FieldValueType


class FilterOperator(StrEnum):
    """Enumeration of all available filter operators."""

    # Comparison operators
    EQ = "eq"  # equals
    NE = "ne"  # not equals

    # Text operators
    CONTAINS = "contains"  # substring search
    STARTSWITH = "startswith"  # starts with text
    ENDSWITH = "endswith"  # ends with text

    # List/Set operators
    IN = "in"  # value in list/has any of
    ALL = "all"  # has all values

    # Numeric/Date comparison operators
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal


class FilterCondition(BaseModel):
    field: str  # field name to filter on
    operator: FilterOperator  # eq, ne, gt, lt, contains, in, etc.
    value: FieldValueType  # value to compare against


class Filter(BaseModel):
    id: str  # unique identifier within space: "urgent-tasks", "my-drafts"
    title: str  # human-readable title: "Urgent Tasks", "My Drafts"
    description: str = ""  # optional description/comment
    conditions: list[FilterCondition]  # filter conditions
    sort: list[str] = []  # ["name", "-created_at", "priority"]
    list_fields: list[str] = []  # columns to display
