from fastapi import APIRouter

from spacenote.core.space.models import Space
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import ApiView

router: APIRouter = APIRouter()


@cbv(router)
class SpacesRouter(ApiView):
    @router.get("/spaces", response_model_by_alias=False)
    async def list_spaces(self) -> list[Space]:
        return await self.app.get_spaces_by_member(self.session_id)
