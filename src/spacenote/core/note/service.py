from datetime import UTC, datetime
from typing import Any

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.field.validators import validate_note_fields
from spacenote.core.filter.mongo import build_mongodb_query, build_sort_spec
from spacenote.core.note.models import Note, PaginationResult
from spacenote.core.user.models import User


class NoteService(Service):
    """Service for managing spaces with in-memory caching."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)
        self._collections: dict[str, AsyncCollection[dict[str, Any]]] = {}

    def add_collection(self, space_id: str) -> None:
        """Add a new collection for a space."""
        self._collections[space_id] = self.database.get_collection(f"{space_id}_notes")

    async def on_start(self) -> None:
        """Initialize service on application startup."""
        for space in self.core.services.space.get_spaces():
            self._collections[space.id] = self.database.get_collection(f"{space.id}_notes")

    async def list_notes(
        self, space_id: str, filter_id: str | None = None, current_user: User | None = None, page: int = 1, page_size: int = 20
    ) -> PaginationResult:
        """List notes in a space with optional filter and pagination."""
        collection = self._collections[space_id]

        # Build query and sort based on filter
        if filter_id:
            space = self.core.services.space.get_space(space_id)
            filter = space.get_filter(filter_id)
            if not filter:
                raise ValueError(f"Filter '{filter_id}' not found in space")

            query = build_mongodb_query(filter, space, current_user)
            sort_spec = build_sort_spec(filter)
        else:
            query = {}
            sort_spec = [("_id", -1)]

        # Get total count
        total_count = await collection.count_documents(query)

        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size

        # Get paginated results
        cursor = collection.find(query)
        for field, direction in sort_spec:
            cursor = cursor.sort(field, direction)
        cursor = cursor.skip(skip).limit(page_size)

        notes = await Note.list_cursor(cursor)

        return PaginationResult(
            notes=notes,
            total_count=total_count,
            current_page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    async def create_note_from_raw_fields(self, space_id: str, author: str, raw_fields: dict[str, str]) -> Note:
        """Create a new note in a space from raw field values (validates and converts)."""
        space = self.core.services.space.get_space(space_id)

        # Get the next auto-increment ID for this space
        last_note = await self._collections[space_id].find({}).sort("_id", -1).limit(1).to_list(1)
        next_id = 1 if not last_note else last_note[0]["_id"] + 1

        note = Note(
            id=next_id,
            author=author,
            created_at=datetime.now(UTC),
            fields=validate_note_fields(space, raw_fields, skip_missing=True),
        )
        await self._collections[space_id].insert_one(note.to_dict())
        return note

    async def get_note(self, space_id: str, note_id: int) -> Note:
        """Get a single note by ID from a space."""
        res = await self._collections[space_id].find_one({"_id": note_id})
        if res:
            return Note.model_validate(res)
        raise ValueError(f"Note with ID {note_id} not found in space {space_id}")

    async def update_comment_stats(self, space_id: str, note_id: int, last_comment_date: datetime) -> None:
        """Update comment statistics for a note after a new comment is added."""
        await self._collections[space_id].update_one(
            {"_id": note_id}, {"$inc": {"comment_count": 1}, "$set": {"last_comment_at": last_comment_date}}
        )

    async def update_note_from_raw_fields(self, space_id: str, note_id: int, raw_fields: dict[str, str]) -> Note:
        """Update an existing note in a space from raw field values (validates and converts)."""
        space = self.core.services.space.get_space(space_id)
        validated_fields = validate_note_fields(space, raw_fields, skip_missing=False)
        await self._collections[space_id].update_one(
            {"_id": note_id}, {"$set": {"fields": validated_fields, "edited_at": datetime.now(UTC)}}
        )
        return await self.get_note(space_id, note_id)

    async def drop_collection(self, space_id: str) -> None:
        """Drop the entire collection for a space."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")
        await self._collections[space_id].drop()
        del self._collections[space_id]

    async def count_notes(self, space_id: str) -> int:
        """Count the number of notes in a space."""
        if space_id not in self._collections:
            raise ValueError(f"Collection for space '{space_id}' does not exist")
        return await self._collections[space_id].count_documents({})
