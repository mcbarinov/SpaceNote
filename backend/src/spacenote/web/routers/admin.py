import json
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import SessionView
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/admin")


@cbv(router)
class Pages(SessionView):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        return await self.render.html("admin/index.j2")

    @router.get("/users")
    async def users(self) -> HTMLResponse:
        users = await self.app.get_users(self.session_id)
        return await self.render.html("admin/users.j2", users=users)

    @router.get("/spaces")
    async def spaces(self) -> HTMLResponse:
        spaces = await self.app.get_all_spaces(self.session_id)
        return await self.render.html("admin/spaces.j2", spaces=spaces)

    @router.get("/telegram")
    async def telegram_bots(self) -> HTMLResponse:
        bots = await self.app.get_telegram_bots(self.session_id)
        return await self.render.html("admin/telegram-bots.j2", bots=bots)

    @router.get("/telegram/create")
    async def create_telegram_bot(self) -> HTMLResponse:
        return await self.render.html("admin/create-telegram-bot.j2")

    @router.get("/users/create")
    async def create_user(self) -> HTMLResponse:
        return await self.render.html("admin/create-user.j2")

    @router.get("/spaces/import")
    async def import_form(self) -> HTMLResponse:
        return await self.render.html("admin/import.j2")

    @router.get("/spaces/{space_id}/export")
    async def export(self, space_id: str, include_content: bool = False) -> PlainTextResponse:
        export_data = await self.app.export_space_as_json(self.session_id, space_id, include_content)
        # Convert dict to JSON string
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        return PlainTextResponse(content=json_content, media_type="application/json")

    @router.get("/spaces/{space_id}/delete", name="admin_delete_space", response_model=None)
    async def delete_space(self, space_id: str) -> HTMLResponse | RedirectResponse:
        spaces = await self.app.get_all_spaces(self.session_id)
        space = next((s for s in spaces if s.id == space_id), None)
        if not space:
            self.render.flash(f"Space '{space_id}' not found", is_error=True)
            return redirect("/admin/spaces")

        # Count notes and comments
        note_count = await self.app.count_space_notes(self.session_id, space_id)
        comment_count = await self.app.count_space_comments(self.session_id, space_id)

        return await self.render.html("admin/delete-space.j2", space=space, note_count=note_count, comment_count=comment_count)


@cbv(router)
class AdminActionRouter(SessionView):
    class CreateUserForm(BaseModel):
        username: str
        password: str

    class ImportSpaceForm(BaseModel):
        json_content: str

    class CreateTelegramBotForm(BaseModel):
        bot_id: str
        token: str

    @router.post("/users/create")
    async def create_user_action(self, form: Annotated[CreateUserForm, Form()]) -> RedirectResponse:
        user = await self.app.create_user(self.session_id, form.username, form.password)
        self.render.flash(f"User '{user.id}' created successfully")
        return redirect("/admin/users")

    @router.post("/spaces/import")
    async def import_space(self, form: Annotated[ImportSpaceForm, Form()]) -> RedirectResponse:
        data = json.loads(form.json_content)
        result = await self.app.import_space_from_json(self.session_id, data)

        # Build success message
        msg = f"Space '{result.space_id}' imported successfully"
        if result.notes_imported > 0:
            msg += f" with {result.notes_imported} notes"
        if result.comments_imported > 0:
            msg += f" and {result.comments_imported} comments"

        self.render.flash(msg)

        # Show warnings if any
        for warning in result.warnings:
            self.render.flash(warning, is_error=False)

        return redirect("/admin/spaces")

    class DeleteSpaceForm(BaseModel):
        space_name: str

    @router.post("/spaces/{space_id}/delete", name="admin_delete_space_post")
    async def delete_space_action(self, space_id: str, value: Annotated[str, Form()]) -> RedirectResponse:
        spaces = await self.app.get_all_spaces(self.session_id)
        space = next((s for s in spaces if s.id == space_id), None)
        if not space:
            self.render.flash(f"Space '{space_id}' not found", is_error=True)
            return redirect("/admin/spaces")

        if value != space.id:
            self.render.flash("Space ID does not match. Deletion cancelled.", is_error=True)
            return redirect(f"/admin/spaces/{space_id}/delete")

        await self.app.delete_space(self.session_id, space_id)
        self.render.flash(f"Space '{space.name}' has been permanently deleted")
        return redirect("/admin/spaces")

    @router.post("/telegram/create")
    async def create_telegram_bot_action(self, form: Annotated[CreateTelegramBotForm, Form()]) -> RedirectResponse:
        bot = await self.app.create_telegram_bot(self.session_id, form.bot_id, form.token)
        self.render.flash(f"Telegram bot '{bot.id}' created successfully")
        return redirect("/admin/telegram")

    @router.post("/telegram/{bot_id}/delete")
    async def delete_telegram_bot_action(self, bot_id: str) -> RedirectResponse:
        await self.app.delete_telegram_bot(self.session_id, bot_id)
        self.render.flash(f"Telegram bot '{bot_id}' deleted successfully")
        return redirect("/admin/telegram")
