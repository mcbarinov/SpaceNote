from fastapi import APIRouter
from pydantic import BaseModel

from spacenote.core.space.models import Space
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import ApiView

router: APIRouter = APIRouter()


class CreateSpaceRequest(BaseModel):
    id: str
    name: str


class UpdateFieldsRequest(BaseModel):
    field_names: list[str]


@cbv(router)
class SpacesRouter(ApiView):
    @router.get("/spaces", response_model_by_alias=False)
    async def list_spaces(self) -> list[Space]:
        return await self.app.get_spaces_by_member(self.session_id)

    @router.get("/spaces/{space_id}", response_model_by_alias=False)
    async def get_space(self, space_id: str) -> Space:
        """Get details of a specific space."""
        return await self.app.get_space(self.session_id, space_id)

    @router.post("/spaces", response_model_by_alias=False)
    async def create_space(self, request: CreateSpaceRequest) -> Space:
        """Create a new space."""
        return await self.app.create_space(self.session_id, request.id, request.name)

    @router.put("/spaces/{space_id}/list-fields")
    async def update_list_fields(self, space_id: str, request: UpdateFieldsRequest) -> None:
        """Update which fields are shown in the notes list."""
        await self.app.update_list_fields(self.session_id, space_id, request.field_names)

    @router.put("/spaces/{space_id}/hidden-create-fields")
    async def update_hidden_create_fields(self, space_id: str, request: UpdateFieldsRequest) -> None:
        """Update which fields are hidden in the create form."""
        await self.app.update_hidden_create_fields(self.session_id, space_id, request.field_names)
