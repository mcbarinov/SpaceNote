from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import SessionView
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/profile")


class ChangePasswordForm(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


@cbv(router)
class ProfileRouter(SessionView):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("profile/index.j2")

    @router.post("/change-password", response_model=None)
    async def change_password(self, form: Annotated[ChangePasswordForm, Form()]) -> HTMLResponse | RedirectResponse:
        await self.app.change_password(self.session_id, form.current_password, form.new_password)
        self.render.flash("Password changed successfully. Please log in again.")
        return redirect("/profile")
