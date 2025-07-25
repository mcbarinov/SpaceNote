from typing import Annotated

from fastapi import APIRouter, Query

from spacenote.core.note.models import Note, PaginationResult
from spacenote.web.deps import AppDep, SessionIdDep

router: APIRouter = APIRouter()


@router.get("/notes", response_model_by_alias=False)
async def list_notes(
    space_id: Annotated[str, Query()],
    app: AppDep,
    session_id: SessionIdDep,
    filter_id: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = None,
) -> PaginationResult:
    """List notes in a space with optional filtering and pagination."""
    return await app.list_notes(session_id, space_id, filter_id, page, page_size)


@router.get("/notes/{note_id}", response_model_by_alias=False)
async def get_note(note_id: int, space_id: Annotated[str, Query()], app: AppDep, session_id: SessionIdDep) -> Note:
    """Get a single note by ID."""
    return await app.get_note(session_id, space_id, note_id)


@router.post("/notes", response_model_by_alias=False)
async def create_note(fields: dict[str, str], space_id: Annotated[str, Query()], app: AppDep, session_id: SessionIdDep) -> Note:
    """Create a new note in a space."""
    return await app.create_note_from_raw_fields(session_id, space_id, fields)


@router.put("/notes/{note_id}", response_model_by_alias=False)
async def update_note(
    note_id: int, fields: dict[str, str], space_id: Annotated[str, Query()], app: AppDep, session_id: SessionIdDep
) -> Note:
    """Update an existing note in a space."""
    return await app.update_note_from_raw_fields(session_id, space_id, note_id, fields)
