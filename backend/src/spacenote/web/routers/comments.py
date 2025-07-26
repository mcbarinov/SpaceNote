from typing import Annotated

from fastapi import APIRouter, Body, Query

from spacenote.core.comment.models import Comment
from spacenote.web.deps import AppDep, SessionIdDep

router: APIRouter = APIRouter()


@router.get("/comments", response_model_by_alias=False)
async def list_comments(
    space_id: Annotated[str, Query()], note_id: Annotated[int, Query()], app: AppDep, session_id: SessionIdDep
) -> list[Comment]:
    """List comments for a specific note."""
    return await app.get_note_comments(session_id, space_id, note_id)


@router.post("/comments", response_model_by_alias=False)
async def create_comment(
    space_id: Annotated[str, Query()],
    note_id: Annotated[int, Query()],
    app: AppDep,
    session_id: SessionIdDep,
    content: Annotated[str, Body(embed=True)],
) -> Comment:
    """Create a new comment for a note."""
    return await app.create_comment(session_id, space_id, note_id, content)
