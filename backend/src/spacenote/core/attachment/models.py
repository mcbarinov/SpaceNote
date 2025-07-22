from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from spacenote.core.db import MongoModel


class MediaCategory(StrEnum):
    """Categories for media files only (images, videos, audio)."""

    IMAGES = "images"
    VIDEOS = "videos"
    AUDIO = "audio"


class AttachmentCategory(StrEnum):
    """All attachment categories including non-media files."""

    IMAGES = "images"
    VIDEOS = "videos"
    AUDIO = "audio"
    DOCUMENTS = "documents"
    OTHER = "other"


class AttachmentCounts(BaseModel):
    """Counts for different types of attachments."""

    total: int = 0
    images: int = 0
    videos: int = 0
    audio: int = 0
    documents: int = 0
    other: int = 0


# Content type mappings
ATTACHMENT_CATEGORIES = {
    AttachmentCategory.IMAGES: {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp",
        "image/tiff",
    },
    AttachmentCategory.VIDEOS: {
        "video/mp4",
        "video/webm",
        "video/avi",
        "video/mov",
        "video/mkv",
        "video/wmv",
        "video/flv",
    },
    AttachmentCategory.AUDIO: {
        "audio/mp3",
        "audio/wav",
        "audio/ogg",
        "audio/m4a",
        "audio/aac",
        "audio/flac",
        "audio/wma",
    },
    AttachmentCategory.DOCUMENTS: {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    },
}

# Media categories (subset of attachment categories)
MEDIA_CATEGORIES = {
    MediaCategory.IMAGES: ATTACHMENT_CATEGORIES[AttachmentCategory.IMAGES],
    MediaCategory.VIDEOS: ATTACHMENT_CATEGORIES[AttachmentCategory.VIDEOS],
    MediaCategory.AUDIO: ATTACHMENT_CATEGORIES[AttachmentCategory.AUDIO],
}


def get_attachment_category(content_type: str) -> AttachmentCategory:
    """Get the category for an attachment based on its content type."""
    for category, types in ATTACHMENT_CATEGORIES.items():
        if content_type in types:
            return category
    return AttachmentCategory.OTHER  # Default fallback for unknown types


def get_media_category(content_type: str) -> MediaCategory | None:
    """Get the media category for an attachment, or None if not media."""
    for category, types in MEDIA_CATEGORIES.items():
        if content_type in types:
            return category
    return None


def is_media(content_type: str) -> bool:
    """Check if an attachment is considered media (images, videos, audio)."""
    return get_media_category(content_type) is not None


class Attachment(MongoModel):
    id: int = Field(alias="_id")  # Auto-incremented within each space
    space_id: str  # Space this attachment belongs to
    filename: str  # Original filename (e.g., "report.pdf")
    content_type: str  # MIME type (e.g., "application/pdf", "image/jpeg")
    size: int  # File size in bytes
    author: str  # User who uploaded the file
    created_at: datetime  # When file was uploaded
    note_id: int | None = None  # Attached note (None = unassigned)

    @property
    def path(self) -> Path:
        """Calculate the relative path from attachments root."""
        filename_parts = Path(self.filename)
        storage_filename = f"{filename_parts.stem}__{self.id}{filename_parts.suffix}"

        if self.note_id is None:
            return Path(self.space_id) / "__unassigned__" / storage_filename
        return Path(self.space_id) / str(self.note_id) / storage_filename

    @property
    def category(self) -> AttachmentCategory:
        """Get the category of this attachment."""
        return get_attachment_category(self.content_type)

    @property
    def media_category(self) -> MediaCategory | None:
        """Get the media category of this attachment, or None if not media."""
        return get_media_category(self.content_type)

    @property
    def is_media(self) -> bool:
        """Check if this attachment is media (images, videos, audio)."""
        return is_media(self.content_type)
