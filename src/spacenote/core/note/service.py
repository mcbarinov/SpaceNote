from typing import Any

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.core import Service
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
