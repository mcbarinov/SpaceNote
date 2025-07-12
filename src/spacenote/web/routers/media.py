from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from spacenote.core.attachment.models import Attachment, MediaCategory
from spacenote.web.class_based_view import cbv
from spacenote.web.deps import View

router: APIRouter = APIRouter(prefix="/media")


@cbv(router)
class MediaPageRouter(View):
    @router.get("/spaces/{space_id}")
    async def media_gallery(self, space_id: str, category: Annotated[MediaCategory | None, Query()] = None) -> HTMLResponse:
        """Display media gallery for a space."""
        space = self.app.get_space(self.current_user, space_id)
        media_attachments = await self.app.get_media_attachments(self.current_user, space_id, category)

        # Group media by category for display
        media_by_category: dict[str, list[Attachment]] = {
            MediaCategory.IMAGES: [],
            MediaCategory.VIDEOS: [],
            MediaCategory.AUDIO: [],
        }

        for attachment in media_attachments:
            if attachment.media_category and attachment.media_category in media_by_category:
                media_by_category[attachment.media_category].append(attachment)

        return await self.render.html(
            "media/gallery.j2",
            space=space,
            media_attachments=media_attachments,
            media_by_category=media_by_category,
            current_category=category,
        )
