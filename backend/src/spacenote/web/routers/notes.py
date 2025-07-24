from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from spacenote.core.note.models import PaginationResult
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import ApiView

router: APIRouter = APIRouter()


@cbv(router)
class NotesRouter(ApiView):
    @router.get("/notes", response_model_by_alias=False)
    async def list_notes(
        self,
        space_id: Annotated[str, Query()],
        filter_id: Annotated[str | None, Query()] = None,
        page: Annotated[int, Query(gt=0)] = 1,
        page_size: Annotated[int | None, Query(gt=0)] = None,
    ) -> PaginationResult:
        """List notes in a space with optional filtering and pagination."""
        try:
            return await self.app.list_notes(self.session_id, space_id, filter_id, page, page_size)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
