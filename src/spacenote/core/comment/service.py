from datetime import UTC, datetime
from typing import Any

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.comment.models import Comment
from spacenote.core.core import Service


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
            raise ValueError("Comment content cannot be empty")

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

        return comment

    async def get_comments_for_note(self, space_id: str, note_id: int) -> list[Comment]:
        """Get all comments for a specific note, ordered by creation time."""
        return await Comment.list_cursor(self._collections[space_id].find({"note_id": note_id}).sort("_id", 1))

    async def drop_collection(self, space_id: str) -> None:
        """Drop the entire collection for a space."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")

        await self._collections[space_id].drop()
        del self._collections[space_id]

    async def count_comments(self, space_id: str) -> int:
        """Count the number of comments in a space."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")
        return await self._collections[space_id].count_documents({})
