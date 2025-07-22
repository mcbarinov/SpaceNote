from enum import StrEnum

from pydantic import BaseModel

# Available values for field options
# - list[str]: for CHOICE field VALUES option (strictly strings)
# - int | float: for numeric field MIN/MAX options
FieldOptionValueType = list[str] | int | float

# Possible values that can be stored in a field
# - str: for STRING, MARKDOWN, CHOICE, USER, DATETIME fields
# - bool: for BOOLEAN fields
# - list[str]: for TAGS fields
# - int: for INT fields and IMAGE fields (attachment_id)
# - float: for FLOAT fields
# - None: for empty/unset fields
FieldValueType = str | bool | list[str] | int | float | None


class FieldType(StrEnum):
    STRING = "string"
    MARKDOWN = "markdown"  # Markdown text with validation and rendering
    BOOLEAN = "boolean"  # True/false values
    CHOICE = "choice"  # Predefined options
    TAGS = "tags"  # List of strings for categorization
    USER = "user"  # User selection from space members
    DATETIME = "datetime"  # Date and time selection
    INT = "int"  # Integer numeric values
    FLOAT = "float"  # Floating-point numeric values
    IMAGE = "image"  # Image attachment reference (attachment_id)
    # ATTACHMENT = "attachment"  # File attachments


class FieldOption(StrEnum):
    VALUES = "values"  # For CHOICE type, list of string options (strictly list[str])
    MIN = "min"  # Minimum value for INT/FLOAT fields (int for INT, int|float for FLOAT)
    MAX = "max"  # Maximum value for INT/FLOAT fields (int for INT, int|float for FLOAT)


class SpaceField(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    options: dict[FieldOption, FieldOptionValueType] = {}
    default: FieldValueType = None
