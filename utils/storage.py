"""
Image storage utility.
Local dev: saves to uploads/ folder with WebP conversion.
Production: swap to Google Cloud Storage.
"""
import os
import uuid
from io import BytesIO
from typing import Tuple

from PIL import Image

from config import UPLOADS_DIR, THUMBNAIL_WIDTH, MAX_IMAGE_SIZE, ALLOWED_IMAGE_TYPES


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_image(file_content: bytes, content_type: str, recipe_id: str = "temp") -> Tuple[str, str]:
    """
    Save an uploaded image, convert to WebP, create thumbnail.
    Returns (image_url, thumbnail_url) as relative paths.
    """
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Unsupported image type: {content_type}")

    if len(file_content) > MAX_IMAGE_SIZE:
        raise ValueError(f"Image exceeds maximum size of {MAX_IMAGE_SIZE // (1024*1024)}MB")

    recipe_dir = os.path.join(UPLOADS_DIR, recipe_id)
    _ensure_dir(recipe_dir)

    filename = uuid.uuid4().hex[:16]
    image_path = os.path.join(recipe_dir, f"{filename}.webp")
    thumb_path = os.path.join(recipe_dir, f"{filename}_thumb.webp")

    # Open and convert to WebP
    img = Image.open(BytesIO(file_content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Save full-size WebP
    img.save(image_path, "WEBP", quality=85)

    # Create and save thumbnail
    thumb = img.copy()
    ratio = THUMBNAIL_WIDTH / thumb.width
    thumb_height = int(thumb.height * ratio)
    thumb = thumb.resize((THUMBNAIL_WIDTH, thumb_height), Image.Resampling.LANCZOS)
    thumb.save(thumb_path, "WEBP", quality=80)

    # Return relative URLs
    image_url = f"/uploads/{recipe_id}/{filename}.webp"
    thumbnail_url = f"/uploads/{recipe_id}/{filename}_thumb.webp"

    return image_url, thumbnail_url


def delete_image(image_url: str) -> bool:
    """Delete an image file by its URL path."""
    if not image_url.startswith("/uploads/"):
        return False

    # Convert URL to file path
    rel_path = image_url.replace("/uploads/", "")
    file_path = os.path.join(UPLOADS_DIR, rel_path)

    if os.path.exists(file_path):
        os.remove(file_path)
        # Also try to delete the thumbnail
        base, ext = os.path.splitext(file_path)
        thumb_path = f"{base}_thumb{ext}"
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        return True
    return False
