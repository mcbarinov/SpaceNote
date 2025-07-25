from fastapi import APIRouter
from pydantic import BaseModel

from spacenote.core.space.models import Space
from spacenote.web.deps import AppDep, SessionIdDep

router: APIRouter = APIRouter()


class CreateSpaceRequest(BaseModel):
    id: str
    name: str


class UpdateFieldsRequest(BaseModel):
    field_names: list[str]


@router.get("/spaces", response_model_by_alias=False)
async def list_spaces(app: AppDep, session_id: SessionIdDep) -> list[Space]:
    return await app.get_spaces_by_member(session_id)


@router.get("/spaces/{space_id}", response_model_by_alias=False)
async def get_space(space_id: str, app: AppDep, session_id: SessionIdDep) -> Space:
    """Get details of a specific space."""
    return await app.get_space(session_id, space_id)


@router.post("/spaces", response_model_by_alias=False)
async def create_space(request: CreateSpaceRequest, app: AppDep, session_id: SessionIdDep) -> Space:
    """Create a new space."""
    return await app.create_space(session_id, request.id, request.name)


@router.put("/spaces/{space_id}/list-fields")
async def update_list_fields(space_id: str, request: UpdateFieldsRequest, app: AppDep, session_id: SessionIdDep) -> None:
    """Update which fields are shown in the notes list."""
    await app.update_list_fields(session_id, space_id, request.field_names)


@router.put("/spaces/{space_id}/hidden-create-fields")
async def update_hidden_create_fields(space_id: str, request: UpdateFieldsRequest, app: AppDep, session_id: SessionIdDep) -> None:
    """Update which fields are hidden in the create form."""
    await app.update_hidden_create_fields(session_id, space_id, request.field_names)
