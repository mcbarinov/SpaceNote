from typing import Annotated

import structlog
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import SessionView
from spacenote.web.utils import redirect

logger = structlog.get_logger(__name__)

router: APIRouter = APIRouter(prefix="/notes")


@cbv(router)
class NotePageRouter(SessionView):
    @router.get("/")
    async def index(self) -> HTMLResponse:
        spaces = await self.app.get_spaces_by_member(self.session_id)
        return await self.render.html("notes/index.j2", spaces=spaces)

    @router.get("/{space_id}")
    async def list_notes(
        self, space_id: str, filter: str | None = None, page: int = 1, page_size: int | None = None
    ) -> HTMLResponse:
        log = logger.bind(space_id=space_id, filter=filter, page=page, page_size=page_size)
        space = await self.app.get_space(self.session_id, space_id)
        pagination_result = await self.app.list_notes(self.session_id, space_id, filter, page, page_size)
        log.debug("listing_notes", pagination_result=pagination_result)

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
        space = await self.app.get_space(self.session_id, space_id)
        unassigned_attachments = await self.app.get_space_attachments(self.session_id, space_id, unassigned_only=True)
        unassigned_image_attachments = [att for att in unassigned_attachments if att.category.value == "images"]
        return await self.render.html("notes/create.j2", space=space, unassigned_image_attachments=unassigned_image_attachments)

    @router.get("/{space_id}/{note_id}")
    async def view_note(self, space_id: str, note_id: int) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        note = await self.app.get_note(self.session_id, space_id, note_id)
        comments = await self.app.get_note_comments(self.session_id, space_id, note_id)
        return await self.render.html("notes/view.j2", space=space, note=note, comments=comments)

    @router.get("/{space_id}/{note_id}/edit")
    async def edit_note_form(self, space_id: str, note_id: int) -> HTMLResponse:
        space = await self.app.get_space(self.session_id, space_id)
        note = await self.app.get_note(self.session_id, space_id, note_id)
        unassigned_attachments = await self.app.get_space_attachments(self.session_id, space_id, unassigned_only=True)
        unassigned_image_attachments = [att for att in unassigned_attachments if att.category.value == "images"]
        note_attachments = await self.app.get_note_attachments(self.session_id, space_id, note_id)
        note_image_attachments = [att for att in note_attachments if att.category.value == "images"]
        return await self.render.html(
            "notes/edit.j2",
            space=space,
            note=note,
            unassigned_image_attachments=unassigned_image_attachments,
            note_image_attachments=note_image_attachments,
        )


@cbv(router)
class NoteActionRouter(SessionView):
    @router.post("/{space_id}/create")
    async def create_note(self, space_id: str, request: Request) -> RedirectResponse:
        form_data = await request.form()
        space = await self.app.get_space(self.session_id, space_id)

        raw_fields = {}
        for key, value in form_data.items():
            if key.startswith("field_"):
                field_name = key[6:]  # Remove "field_" prefix
                # Convert UploadFile to string if needed
                field_value = value if isinstance(value, str) else ""

                # Skip empty fields that have default values - let them use defaults
                field_def = space.get_field(field_name)
                if field_def and field_def.default is not None and not field_value:
                    continue

                raw_fields[field_name] = field_value

        await self.app.create_note_from_raw_fields(self.session_id, space_id, raw_fields)
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

        await self.app.update_note_from_raw_fields(self.session_id, space_id, note_id, raw_fields)
        self.render.flash("Note updated successfully")
        return redirect(f"/notes/{space_id}/{note_id}")

    @router.post("/{space_id}/{note_id}/comments")
    async def create_comment(self, space_id: str, note_id: int, content: Annotated[str, Form()]) -> RedirectResponse:
        await self.app.create_comment(self.session_id, space_id, note_id, content.strip())
        self.render.flash("Comment added successfully")
        return redirect(f"/notes/{space_id}/{note_id}")
