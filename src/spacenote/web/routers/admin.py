from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/admin")


@cbv(router)
class Pages(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("admin/index.j2")

    @router.get("/users")
    async def users(self) -> HTMLResponse:
        users = self.app.get_users(self.current_user)
        return await self.render.html("admin/users.j2", users=users)

    @router.get("/spaces")
    async def spaces(self) -> HTMLResponse:
        spaces = self.app.get_all_spaces(self.current_user)
        return await self.render.html("admin/spaces.j2", spaces=spaces)

    @router.get("/users/create")
    async def create_user(self) -> HTMLResponse:
        return await self.render.html("admin/create-user.j2")

    @router.get("/spaces/{space_id}/delete", name="admin_delete_space", response_model=None)
    async def delete_space(self, space_id: str) -> HTMLResponse | RedirectResponse:
        spaces = self.app.get_all_spaces(self.current_user)
        space = next((s for s in spaces if s.id == space_id), None)
        if not space:
            self.render.flash(f"Space '{space_id}' not found", is_error=True)
            return redirect("/admin/spaces")

        # Count notes and comments
        note_count = await self.app.count_space_notes(self.current_user, space_id)
        comment_count = await self.app.count_space_comments(self.current_user, space_id)

        return await self.render.html("admin/delete-space.j2", space=space, note_count=note_count, comment_count=comment_count)


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

    class DeleteSpaceForm(BaseModel):
        space_name: str

    @router.post("/spaces/{space_id}/delete", name="admin_delete_space_post")
    async def delete_space_action(self, space_id: str, value: Annotated[str, Form()]) -> RedirectResponse:
        space = self.app.get_space(self.current_user, space_id)
        if value != space.name:
            self.render.flash("Space name does not match. Deletion cancelled.", is_error=True)
            return redirect(f"/admin/spaces/{space_id}/delete")

        await self.app.delete_space(self.current_user, space_id)
        self.render.flash(f"Space '{space.name}' has been permanently deleted")
        return redirect("/admin/spaces")
