from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import SessionView
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/attachments")


@cbv(router)
class AttachmentPageRouter(SessionView):
    @router.get("/spaces/{space_id}")
    async def list_attachments(self, space_id: str) -> HTMLResponse:
        """List unassigned attachments for a space."""
        space = await self.app.get_space(self.session_id, space_id)
        attachments = await self.app.get_space_attachments(self.session_id, space_id, unassigned_only=True)
        return await self.render.html("attachments/list.j2", space=space, attachments=attachments)

    @router.post("/spaces/{space_id}/upload")
    async def upload_attachment(self, space_id: str, file: Annotated[UploadFile, File()]) -> RedirectResponse:
        """Upload a file attachment to a space."""
        await self.app.upload_attachment(self.session_id, space_id, file)
        return redirect(f"/attachments/spaces/{space_id}")

    @router.get("/spaces/{space_id}/download/{attachment_id}")
    async def download_attachment(self, space_id: str, attachment_id: int) -> FileResponse:
        """Download a file attachment."""
        attachment = await self.app.get_attachment(self.session_id, space_id, attachment_id)

        file_path = await self.app.get_attachment_file_path(self.session_id, attachment)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")

        return FileResponse(
            path=file_path,
            filename=attachment.filename,
            media_type=attachment.content_type,
        )

    @router.get("/spaces/{space_id}/preview/{attachment_id}")
    async def get_attachment_preview(self, space_id: str, attachment_id: int) -> FileResponse:
        """Get a preview image for an attachment."""
        attachment = await self.app.get_attachment(self.session_id, space_id, attachment_id)

        # Only serve previews for image attachments
        if not attachment.media_category == "images":
            raise HTTPException(status_code=404, detail="Preview not available for this file type")

        preview_path = await self.app.get_attachment_preview_path(self.session_id, attachment)
        if not preview_path.exists():
            raise HTTPException(status_code=404, detail="Preview not found")

        return FileResponse(
            path=preview_path,
            media_type="image/jpeg",
        )

    @router.post("/spaces/{space_id}/assign/{attachment_id}/note/{note_id}")
    async def assign_attachment_to_note(self, space_id: str, attachment_id: int, note_id: int) -> RedirectResponse:
        """Assign an attachment to a specific note."""
        await self.app.assign_attachment_to_note(self.session_id, space_id, attachment_id, note_id)
        return redirect(f"/notes/{space_id}/{note_id}")

    @router.get("/spaces/{space_id}/notes/{note_id}")
    async def get_note_attachments(self, space_id: str, note_id: int) -> HTMLResponse:
        """Get attachments for a specific note."""
        space = await self.app.get_space(self.session_id, space_id)
        note = await self.app.get_note(self.session_id, space_id, note_id)
        attachments = await self.app.get_note_attachments(self.session_id, space_id, note_id)
        return await self.render.html("attachments/note_attachments.j2", space=space, note=note, attachments=attachments)

    @router.get("/spaces/{space_id}/assign/{attachment_id}")
    async def show_assign_form(self, space_id: str, attachment_id: int) -> HTMLResponse:
        """Show form to assign attachment to a note."""
        space = await self.app.get_space(self.session_id, space_id)
        attachment = await self.app.get_attachment(self.session_id, space_id, attachment_id)
        notes_result = await self.app.list_notes(self.session_id, space_id, page=1, page_size=1000)
        notes = notes_result.notes
        return await self.render.html("attachments/assign.j2", space=space, attachment=attachment, notes=notes)

    @router.post("/spaces/{space_id}/delete/{attachment_id}")
    async def delete_attachment(self, space_id: str, attachment_id: int) -> RedirectResponse:
        """Delete an attachment."""
        await self.app.delete_attachment(self.session_id, space_id, attachment_id)
        return redirect(f"/attachments/spaces/{space_id}")
