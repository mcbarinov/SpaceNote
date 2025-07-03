from enum import StrEnum

from spacenote.core.field.models import FieldType
from spacenote.core.filter.models import Filter, FilterCondition
from spacenote.core.space.models import Space
from spacenote.core.user.models import User


class SpecialValue(StrEnum):
    CURRENT_USER = "@me"


def resolve_special_values(filter: Filter, space: Space, current_user: User | None) -> Filter:
    """Resolve special values in filter conditions based on current context."""
    if not current_user:
        return filter

    resolved_conditions = []

    for condition in filter.conditions:
        if condition.value == SpecialValue.CURRENT_USER:
            field = space.get_field(condition.field)
            if field and field.type == FieldType.USER:
                resolved_conditions.append(
                    FilterCondition(
                        field=condition.field,
                        operator=condition.operator,
                        value=current_user.id,
                    )
                )
            else:
                resolved_conditions.append(condition)
        else:
            resolved_conditions.append(condition)

    return Filter(
        id=filter.id,
        title=filter.title,
        description=filter.description,
        conditions=resolved_conditions,
        sort=filter.sort,
        list_fields=filter.list_fields,
    )
