from enum import StrEnum


class SpecialValue(StrEnum):
    """Special values that can be used in various contexts (filters, defaults, etc)."""

    CURRENT_USER = "@me"
    LAST = "@last"
