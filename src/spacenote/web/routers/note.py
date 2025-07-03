from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/notes")


@cbv(router)
class NotePageRouter(View):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        spaces = self.app.get_spaces_by_member(self.current_user)
        return await self.render.html("notes/index.j2", spaces=spaces)

    @router.get("/{space_id}")
    async def list_notes(
        self, space_id: str, filter: str | None = None, page: int = 1, page_size: int | None = None
    ) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        pagination_result = await self.app.list_notes(self.current_user, space_id, filter, page, page_size)

        # Get the current filter object if filter ID is provided
        current_filter_obj = None
        list_fields = space.list_fields
        if filter:
            current_filter_obj = space.get_filter(filter)
            if current_filter_obj and current_filter_obj.list_fields:
                # Use filter's list fields if defined
                list_fields = current_filter_obj.list_fields

        return await self.render.html(
            "notes/list.j2",
            space=space,
            pagination=pagination_result,
            current_filter=filter,
            list_fields=list_fields,
        )

    @router.get("/{space_id}/create")
    async def create_note_form(self, space_id: str) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        return await self.render.html("notes/create.j2", space=space)

    @router.get("/{space_id}/{note_id}")
    async def view_note(self, space_id: str, note_id: int) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        note = await self.app.get_note(self.current_user, space_id, note_id)
        comments = await self.app.get_note_comments(self.current_user, space_id, note_id)
        return await self.render.html("notes/view.j2", space=space, note=note, comments=comments)

    @router.get("/{space_id}/{note_id}/edit")
    async def edit_note_form(self, space_id: str, note_id: int) -> HTMLResponse:
        space = self.app.get_space(self.current_user, space_id)
        note = await self.app.get_note(self.current_user, space_id, note_id)
        return await self.render.html("notes/edit.j2", space=space, note=note)


@cbv(router)
class NoteActionRouter(View):
    @router.post("/{space_id}/create")
    async def create_note(self, space_id: str, request: Request) -> RedirectResponse:
        form_data = await request.form()

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

    @router.post("/{space_id}/{note_id}/edit")
    async def edit_note(self, space_id: str, note_id: int, request: Request) -> RedirectResponse:
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

        await self.app.update_note_from_raw_fields(self.current_user, space_id, note_id, raw_fields)
        self.render.flash("Note updated successfully")
        return redirect(f"/notes/{space_id}/{note_id}")

    @router.post("/{space_id}/{note_id}/comments")
    async def create_comment(self, space_id: str, note_id: int, content: Annotated[str, Form()]) -> RedirectResponse:
        await self.app.create_comment(self.current_user, space_id, note_id, content.strip())
        self.render.flash("Comment added successfully")
        return redirect(f"/notes/{space_id}/{note_id}")
