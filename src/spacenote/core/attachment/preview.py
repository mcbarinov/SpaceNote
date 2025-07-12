"""Image preview generation utilities."""

import asyncio
from pathlib import Path

import structlog
from PIL import Image

logger = structlog.get_logger(__name__)

PREVIEW_MAX_SIZE = 800
PREVIEW_QUALITY = 85
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def is_image(content_type: str) -> bool:
    """Check if content type is a supported image format."""
    return content_type in SUPPORTED_IMAGE_TYPES


def get_preview_path(original_path: Path, preview_root: Path) -> Path:
    """Get the preview path for an attachment file."""
    # Find the attachments root in the original path
    path_parts = original_path.parts

    # Find where the space_id starts (after attachments directory)
    for i, _part in enumerate(path_parts):
        if i > 0 and path_parts[i - 1].endswith("attachments"):
            # Space ID and everything after
            relative_parts = path_parts[i:]
            relative_path = Path(*relative_parts)
            return preview_root / relative_path

    # Fallback: assume the path structure matches what we expect
    # If original is /path/to/attachments/space_id/folder/file.ext
    # We want /path/to/attachments_preview/space_id/folder/file.ext
    relative_path = Path(*original_path.parts[-3:])  # space_id/folder/file.ext
    return preview_root / relative_path


async def generate_preview(original_path: Path, preview_path: Path) -> None:
    """Generate a preview image from the original file."""
    log = logger.bind(original_path=str(original_path), preview_path=str(preview_path))
    log.debug("generating_preview")

    try:
        # Ensure preview directory exists
        preview_path.parent.mkdir(parents=True, exist_ok=True)

        # Run the blocking image processing in a thread
        await asyncio.to_thread(_create_preview, original_path, preview_path)

        log.debug("preview_generated_successfully")
    except Exception as e:
        log.exception("preview_generation_failed", error=str(e))
        raise


def _create_preview(original_path: Path, preview_path: Path) -> None:
    """Synchronous image processing function."""
    with Image.open(original_path) as original_img:
        # Convert to RGB if necessary (for JPEG output)
        if original_img.mode in ("RGBA", "P"):
            # Create white background for transparency
            background = Image.new("RGB", original_img.size, (255, 255, 255))
            if original_img.mode == "P":
                rgba_img = original_img.convert("RGBA")
                background.paste(rgba_img, mask=rgba_img.split()[-1])
            else:
                background.paste(original_img, mask=original_img.split()[-1])
            processed_img = background
        elif original_img.mode != "RGB":
            processed_img = original_img.convert("RGB")
        else:
            processed_img = original_img.copy()

        # Calculate new size maintaining aspect ratio
        processed_img.thumbnail((PREVIEW_MAX_SIZE, PREVIEW_MAX_SIZE), Image.Resampling.LANCZOS)

        # Save as JPEG with specified quality
        processed_img.save(preview_path, "JPEG", quality=PREVIEW_QUALITY, optimize=True)
