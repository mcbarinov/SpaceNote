from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from spacenote.core.space.models import Space
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import ApiView

router: APIRouter = APIRouter()


class CreateSpaceRequest(BaseModel):
    id: str
    name: str


@cbv(router)
class SpacesRouter(ApiView):
    @router.get("/spaces", response_model_by_alias=False)
    async def list_spaces(self) -> list[Space]:
        return await self.app.get_spaces_by_member(self.session_id)

    @router.get("/spaces/{space_id}", response_model_by_alias=False)
    async def get_space(self, space_id: str) -> Space:
        """Get details of a specific space."""
        try:
            return await self.app.get_space(self.session_id, space_id)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @router.post("/spaces", response_model_by_alias=False)
    async def create_space(self, request: CreateSpaceRequest) -> Space:
        """Create a new space."""
        try:
            return await self.app.create_space(self.session_id, request.id, request.name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e)) from e
