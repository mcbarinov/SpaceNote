from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View

router: APIRouter = APIRouter(prefix="/notes")


@cbv(router)
class NoteRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("notes/index.j2")
