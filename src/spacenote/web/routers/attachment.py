from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View
from spacenote.web.utils import redirect

router: APIRouter = APIRouter(prefix="/attachments")


@cbv(router)
class AttachmentPageRouter(View):
    @router.get("/spaces/{space_id}")
    async def list_attachments(self, space_id: str) -> HTMLResponse:
        """List unassigned attachments for a space."""
        space = self.app.get_space(self.current_user, space_id)
        attachments = await self.app.get_space_attachments(self.current_user, space_id, unassigned_only=True)
        return await self.render.html("attachments/list.j2", space=space, attachments=attachments)

    @router.post("/spaces/{space_id}/upload")
    async def upload_attachment(self, space_id: str, file: Annotated[UploadFile, File()]) -> RedirectResponse:
        """Upload a file attachment to a space."""
        await self.app.upload_attachment(self.current_user, space_id, file)
        return redirect(f"/attachments/spaces/{space_id}")
