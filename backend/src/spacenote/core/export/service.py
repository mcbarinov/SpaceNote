from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from spacenote.core.comment.models import Comment
from spacenote.core.core import Service
from spacenote.core.errors import ValidationError
from spacenote.core.export.models import ExportData, ImportResult
from spacenote.core.export.validators import validate_import_data
from spacenote.core.note.models import Note


class ExportService(Service):
    """Service for exporting and importing space data."""

    def __init__(self, database: AsyncDatabase[dict[str, Any]]) -> None:
        super().__init__(database)

    async def export_space(self, space_id: str, include_content: bool = False) -> dict[str, Any]:
        """Export space with optional notes and comments."""
        space = self.core.services.space.get_space(space_id)

        notes: list[Note] = []
        comments: list[Comment] = []

        if include_content:
            # Export all notes - get all pages
            page = 1
            while True:
                result = await self.core.services.note.list_notes(space_id, page=page, page_size=100)
                notes.extend(result.notes)
                if not result.has_next:
                    break
                page += 1

            # Export all comments - need to get comments for each note
            for note in notes:
                note_comments = await self.core.services.comment.get_comments_for_note(space_id, note.id)
                comments.extend(note_comments)

        export_data = ExportData(version="1.0", space=space, notes=notes, comments=comments)

        return export_data.model_dump()

    async def import_space(self, data: dict[str, Any], importing_user: str) -> ImportResult:  # noqa: PLR0915
        """Import space with optional notes and comments."""
        validation_errors = await validate_import_data(data, self.core.services.space)
        if validation_errors:
            raise ValidationError(f"Import validation failed: {'; '.join(validation_errors)}")

        export_data = ExportData(**data)
        warnings: list[str] = []

        # Create space with basic info
        await self.core.services.space.create_space(export_data.space.id, export_data.space.name, importing_user)

        # Add fields one by one
        for field in export_data.space.fields:
            await self.core.services.space.add_field(export_data.space.id, field)

        # Update list fields
        if export_data.space.list_fields:
            await self.core.services.space.update_list_fields(export_data.space.id, export_data.space.list_fields)

        # Add filters
        for filter in export_data.space.filters:
            await self.core.services.space.add_filter(export_data.space.id, filter)

        # Import notes only if they exist in data
        note_id_mapping: dict[int, int] = {}  # old_id -> new_id
        notes_imported = 0

        for note_data in export_data.notes:
            # Check if author exists, otherwise use importing user
            author = note_data.author
            try:
                user = self.core.services.user.get_user(author)
            except Exception:
                user = None
            if not user:
                author = importing_user
                warnings.append(f"Note {note_data.id}: author '{note_data.author}' not found, using importing user")

            # Create note
            note = Note(
                id=note_data.id,  # Try to preserve ID
                author=author,
                created_at=note_data.created_at,
                fields=note_data.fields,
            )

            # Check if ID already exists
            try:
                await self.core.services.note.get_note(export_data.space.id, note_data.id)
                # ID exists, create with auto-generated ID
                # Convert fields to string format for raw_fields
                raw_fields = {}
                for k, v in note_data.fields.items():
                    if v is not None:
                        if isinstance(v, list):
                            raw_fields[k] = ",".join(str(item) for item in v)
                        else:
                            raw_fields[k] = str(v)

                created_note = await self.core.services.note.create_note_from_raw_fields(export_data.space.id, author, raw_fields)
                note_id_mapping[note_data.id] = created_note.id
                notes_imported += 1
                warnings.append(f"Note {note_data.id}: ID conflict, assigned new ID {created_note.id}")
            except ValueError:
                # ID doesn't exist, can try to preserve it
                # We'll need to manually insert with specific ID
                collection = self.core.services.note._collections[export_data.space.id]  # noqa: SLF001
                note_dict = note.to_dict()
                note_dict["_id"] = note_data.id
                await collection.insert_one(note_dict)
                note_id_mapping[note_data.id] = note_data.id
                notes_imported += 1

        # Import comments
        comments_imported = 0

        for comment_data in export_data.comments:
            # Map note_id
            if comment_data.note_id not in note_id_mapping:
                warnings.append(f"Comment {comment_data.id}: note_id {comment_data.note_id} not found in import, skipping")
                continue

            # Check if author exists
            author = comment_data.author
            try:
                user = self.core.services.user.get_user(author)
            except Exception:
                user = None
            if not user:
                author = importing_user
                warnings.append(f"Comment {comment_data.id}: author '{comment_data.author}' not found, using importing user")

            # Create comment
            comment = Comment(
                id=comment_data.id,
                note_id=note_id_mapping[comment_data.note_id],
                author=author,
                content=comment_data.content,
                created_at=comment_data.created_at,
                edited_at=comment_data.edited_at,
                parent_id=comment_data.parent_id,
            )

            # Similar approach - try to preserve ID
            collection = self.core.services.comment._collections[export_data.space.id]  # noqa: SLF001
            comment_dict = comment.to_dict()
            comment_dict["_id"] = int(comment_data.id)  # Comments use int IDs
            await collection.insert_one(comment_dict)
            comments_imported += 1

            # Update note comment stats
            await self.core.services.note.update_comment_stats(export_data.space.id, comment.note_id, comment.created_at)

        return ImportResult(
            space_id=export_data.space.id, notes_imported=notes_imported, comments_imported=comments_imported, warnings=warnings
        )
