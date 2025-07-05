from datetime import UTC, datetime
from typing import Any

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
from spacenote.core.field.validators import validate_note_fields
from spacenote.core.note.models import Note


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
        # This method can be used to perform any necessary setup when the service starts
        for space in self.core.services.space.get_spaces():
            self._collections[space.id] = self.database.get_collection(f"{space.id}_notes")

    async def list_notes(self, space_id: str) -> list[Note]:
        """List all notes in a space."""
        return await Note.list_cursor(self._collections[space_id].find({}).sort("_id", -1))

    async def create_note_from_raw_fields(self, space_id: str, author: str, raw_fields: dict[str, str]) -> Note:
        """Create a new note in a space from raw field values (validates and converts)."""
        space = self.core.services.space.get_space(space_id)

        # Get the next auto-increment ID for this space
        last_note = await self._collections[space_id].find({}).sort("_id", -1).limit(1).to_list(1)
        next_id = 1 if not last_note else last_note[0]["_id"] + 1

        note = Note(id=next_id, author=author, created_at=datetime.now(UTC), fields=validate_note_fields(space, raw_fields))
        await self._collections[space_id].insert_one(note.to_dict())
        return note

    async def get_note(self, space_id: str, note_id: int) -> Note:
        """Get a single note by ID from a space."""
        res = await self._collections[space_id].find_one({"_id": note_id})
        if res:
            return Note.model_validate(res)
        raise ValueError(f"Note with ID {note_id} not found in space {space_id}")
