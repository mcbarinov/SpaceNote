from datetime import UTC, datetime
from typing import Any

import structlog
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.comment.models import Comment
from spacenote.core.core import Service
from spacenote.core.errors import ValidationError

logger = structlog.get_logger(__name__)


class CommentService(Service):
    """Service for managing comments with per-space collections."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collections: dict[str, AsyncCollection[dict[str, Any]]] = {}

    def add_collection(self, space_id: str) -> None:
        """Add a new collection for a space."""
        self._collections[space_id] = self.database.get_collection(f"{space_id}_comments")

    async def on_start(self) -> None:
        """Initialize service on application startup."""
        for space in self.core.services.space.get_spaces():
            self.add_collection(space.id)

    async def create_comment(self, space_id: str, note_id: int, author: str, content: str) -> Comment:
        """Create a new comment for a note."""
        # Get the next auto-increment ID for this space
        if not content.strip():
            raise ValidationError("Comment content cannot be empty")

        last_comment = await self._collections[space_id].find({}).sort("_id", -1).limit(1).to_list(1)
        next_id = 1 if not last_comment else last_comment[0]["_id"] + 1

        comment = Comment(
            id=next_id,
            note_id=note_id,
            author=author,
            content=content,
            created_at=datetime.now(UTC),
        )
        await self._collections[space_id].insert_one(comment.to_dict())
        await self.core.services.note.update_comment_stats(space_id, note_id, comment.created_at)

        # Send Telegram notification if enabled
        await self._send_telegram_notification(space_id, comment, author)

        return comment

    async def get_comments_for_note(self, space_id: str, note_id: int) -> list[Comment]:
        """Get all comments for a specific note, ordered by creation time."""
        return await Comment.list_cursor(self._collections[space_id].find({"note_id": note_id}).sort("_id", 1))

    async def drop_collection(self, space_id: str) -> None:
        """Drop the entire collection for a space."""
        if space_id not in self._collections:
            raise ValidationError(f"Collection for space '{space_id}' does not exist")

        await self._collections[space_id].drop()
        del self._collections[space_id]

    async def _send_telegram_notification(self, space_id: str, comment: Comment, author: str) -> None:
        """Send a Telegram notification for a comment event."""
        try:
            space = self.core.services.space.get_space(space_id)
            if not space.telegram or not space.telegram.enabled:
                return

            # Get the note for context
            note = await self.core.services.note.get_note(space_id, comment.note_id)

            # Prepare template context
            context = {
                "space": space,
                "note": note,
                "comment": comment,
                "author": author,
                "url": f"{self.core.config.base_url.rstrip('/')}/notes/{space_id}/{comment.note_id}",
            }

            # Render and send the message
            message = self.core.services.telegram.render_template(space.telegram.templates.comment, context)
            note_url = f"{self.core.config.base_url.rstrip('/')}/notes/{space_id}/{comment.note_id}"
            await self.core.services.telegram.send_notification(
                space.telegram.bot_id, space.telegram.channel_id, message, note_url
            )
        except Exception as e:
            logger.warning("telegram_notification_failed", error=str(e), space_id=space_id, event_type="comment")

    async def count_comments(self, space_id: str) -> int:
        """Count the number of comments in a space."""
        if space_id not in self._collections:
            raise ValidationError(f"Collection for space '{space_id}' does not exist")
        return await self._collections[space_id].count_documents({})
