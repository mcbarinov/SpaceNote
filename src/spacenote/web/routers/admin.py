from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/admin")


@cbv(router)
class AdminPageRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("admin/index.j2")

    @router.get("/users")
    async def users(self) -> HTMLResponse:
        users = self.app.get_users(self.current_user)
        return await self.render.html("admin/users.j2", users=users)

    @router.get("/users/create")
    async def create_user(self) -> HTMLResponse:
        return await self.render.html("admin/create-user.j2")


@cbv(router)
class AdminActionRouter(View):
    class CreateUserForm(BaseModel):
        username: str
        password: str

    @router.post("/users/create")
    async def create_user_action(self, form: Annotated[CreateUserForm, Form()]) -> RedirectResponse:
        user = await self.app.create_user(self.current_user, form.username, form.password)
        self.render.flash(f"User '{user.id}' created successfully")
        return redirect("/admin/users")
