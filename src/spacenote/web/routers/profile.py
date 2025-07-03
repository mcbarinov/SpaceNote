from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View

router: APIRouter = APIRouter(prefix="/profile")


@cbv(router)
class ProfileRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("profile/index.j2")
