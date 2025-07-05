from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

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

    @router.get("/{space_id}/create")
    async def create_note_form(self, space_id: str) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        return await self.render.html("notes/create.j2", space=space)

    @router.post("/{space_id}/create")
    async def create_note(self, space_id: str, request: Request) -> RedirectResponse:
        try:
            # Get form data from request
            form_data = await request.form()

            # Parse form data into fields dict
            raw_fields = {}
            for key, value in form_data.items():
                if key.startswith("field_"):
                    field_name = key[6:]  # Remove "field_" prefix
                    # Convert UploadFile to string if needed
                    if isinstance(value, str):
                        raw_fields[field_name] = value
                    else:
                        raw_fields[field_name] = ""

            await self.app.create_note_from_raw_fields(self.current_user, space_id, raw_fields)
            self.render.flash("Note created successfully")
            return redirect(f"/notes/{space_id}")
        except ValueError as e:
            self.render.flash(str(e), is_error=True)
            return redirect(f"/notes/{space_id}/create")

    @router.get("/{space_id}/{note_id}")
    async def view_note(self, space_id: str, note_id: int) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        note = await self.app.get_note(self.current_user, space_id, note_id)
        return await self.render.html("notes/view.j2", space=space, note=note)
