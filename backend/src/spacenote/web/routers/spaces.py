from typing import Annotated, Any

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

from spacenote.core.export.models import ImportResult
from spacenote.core.filter.models import Filter
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


@router.put("/spaces/{space_id}/note-detail-template")
async def update_note_detail_template(
    space_id: str, app: AppDep, session_id: SessionIdDep, template: Annotated[str | None, Body(embed=True)]
) -> None:
    """Update note detail template for customizing individual note display."""
    await app.update_note_detail_template(session_id, space_id, template)


@router.put("/spaces/{space_id}/note-list-template")
async def update_note_list_template(
    space_id: str, app: AppDep, session_id: SessionIdDep, template: Annotated[str | None, Body(embed=True)]
) -> None:
    """Update note list template for customizing note list items."""
    await app.update_note_list_template(session_id, space_id, template)


@router.post("/spaces/{space_id}/filters")
async def create_filter(space_id: str, filter: Filter, app: AppDep, session_id: SessionIdDep) -> None:
    """Create a new filter for the space."""
    await app.add_filter(session_id, space_id, filter)


@router.delete("/spaces/{space_id}/filters/{filter_id}")
async def delete_filter(space_id: str, filter_id: str, app: AppDep, session_id: SessionIdDep) -> None:
    """Delete a filter from the space."""
    await app.delete_filter(session_id, space_id, filter_id)


@router.get("/spaces/{space_id}/export")
async def export_space(
    space_id: str, app: AppDep, session_id: SessionIdDep, include_content: Annotated[bool, Query()] = False
) -> dict[str, Any]:
    """Export a space as JSON. Set include_content=true to include notes and comments."""
    return await app.export_space_as_json(session_id, space_id, include_content)


@router.post("/import", response_model_by_alias=False)
async def import_space(app: AppDep, session_id: SessionIdDep, data: dict[str, Any]) -> ImportResult:
    """Import a space from JSON data."""
    return await app.import_space_from_json(session_id, data)
