from fastapi import APIRouter

from spacenote.core.field.models import FieldType
from spacenote.core.filter.constants import get_valid_operators_list_for_field_type
from spacenote.core.space.models import Space
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import ApiView

router: APIRouter = APIRouter(prefix="/api")


@cbv(router)
class Api(ApiView):
    @router.get("/spaces/{id}")
    async def get_space(self, id: str) -> Space:
        return await self.app.get_space(self.session_id, id)

    @router.get("/filter/operators")
    async def get_all_operators_mapping(self) -> dict[str, list[str]]:
        """Get mapping of all field types to their valid operators."""
        result = {}

        # Add all field types
        for field_type in FieldType:
            operators = get_valid_operators_list_for_field_type(field_type.value)
            result[field_type.value] = [op.value for op in operators]

        # Add built-in field types
        for builtin_type in ["id", "author", "created_at"]:
            operators = get_valid_operators_list_for_field_type(builtin_type)
            result[builtin_type] = [op.value for op in operators]

        return result
