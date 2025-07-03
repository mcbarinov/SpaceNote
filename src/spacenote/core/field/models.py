from enum import StrEnum

from pydantic import BaseModel

FieldOptionValue = list[str]
FieldValue = str | bool | list[str] | None


class FieldType(StrEnum):
    STRING = "string"
    MARKDOWN = "markdown"  # Markdown text with validation and rendering
    BOOLEAN = "boolean"  # True/false values
    CHOICE = "choice"  # Predefined options
    TAGS = "tags"  # List of strings for categorization
    USER = "user"  # User selection from space members
    DATETIME = "datetime"  # Date and time selection
    # ATTACHMENT = "attachment"  # File attachments


class FieldOption(StrEnum):
    VALUES = "values"  # For CHOICE type, list of options
    MIN = "min"  # Minimum value for numeric fields
    MAX = "max"  # Maximum value for numeric fields


class SpaceField(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    options: dict[FieldOption, FieldOptionValue] = {}
    default: FieldValue = None
