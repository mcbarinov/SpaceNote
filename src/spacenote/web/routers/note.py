from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View

router: APIRouter = APIRouter(prefix="/notes")


@cbv(router)
class NoteRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        spaces = self.app.get_spaces_by_member(self.current_user)
        return await self.render.html("notes/index.j2", spaces=spaces)

    @router.get("/{space_id}")
    async def list_notes(self, space_id: str) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        notes = await self.app.list_notes(self.current_user, space_id)
        return await self.render.html("notes/list.j2", space=space, notes=notes)
