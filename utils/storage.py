"""
Image storage utility.
Local dev: saves to uploads/ folder with WebP conversion.
Production: Google Cloud Storage with WebP conversion.
"""
import os
import uuid
from io import BytesIO
from typing import Tuple

from PIL import Image

from config import (
    UPLOADS_DIR, THUMBNAIL_WIDTH, MAX_IMAGE_SIZE, ALLOWED_IMAGE_TYPES,
    STORAGE_MODE, GCS_BUCKET_NAME,
)


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _convert_to_webp(file_content: bytes, quality: int = 85, max_width: int = None) -> bytes:
    """Convert image bytes to WebP format, optionally resizing."""
    img = Image.open(BytesIO(file_content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)

    buf = BytesIO()
    img.save(buf, "WEBP", quality=quality)
    return buf.getvalue()


def _make_thumbnail(file_content: bytes) -> bytes:
    """Create a thumbnail from image bytes."""
    return _convert_to_webp(file_content, quality=80, max_width=THUMBNAIL_WIDTH)


def _validate(file_content: bytes, content_type: str):
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"Unsupported image type: {content_type}")
    if len(file_content) > MAX_IMAGE_SIZE:
        raise ValueError(f"Image exceeds maximum size of {MAX_IMAGE_SIZE // (1024*1024)}MB")


# ── Local storage ────────────────────────────────────────────────

def _save_local(file_content: bytes, content_type: str, recipe_id: str) -> Tuple[str, str]:
    recipe_dir = os.path.join(UPLOADS_DIR, recipe_id)
    _ensure_dir(recipe_dir)

    filename = uuid.uuid4().hex[:16]
    image_path = os.path.join(recipe_dir, f"{filename}.webp")
    thumb_path = os.path.join(recipe_dir, f"{filename}_thumb.webp")

    webp_bytes = _convert_to_webp(file_content)
    thumb_bytes = _make_thumbnail(file_content)

    with open(image_path, "wb") as f:
        f.write(webp_bytes)
    with open(thumb_path, "wb") as f:
        f.write(thumb_bytes)

    image_url = f"/uploads/{recipe_id}/{filename}.webp"
    thumbnail_url = f"/uploads/{recipe_id}/{filename}_thumb.webp"
    return image_url, thumbnail_url


def _delete_local(image_url: str) -> bool:
    if not image_url.startswith("/uploads/"):
        return False

    rel_path = image_url.replace("/uploads/", "")
    file_path = os.path.join(UPLOADS_DIR, rel_path)

    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False

    base, ext = os.path.splitext(file_path)
    thumb_path = f"{base}_thumb{ext}"
    try:
        os.remove(thumb_path)
    except FileNotFoundError:
        pass
    return True


# ── GCS storage ──────────────────────────────────────────────────

_gcs_bucket = None


def _get_gcs_bucket():
    global _gcs_bucket
    if _gcs_bucket is None:
        from google.cloud import storage as gcs
        client = gcs.Client()
        _gcs_bucket = client.bucket(GCS_BUCKET_NAME)
    return _gcs_bucket


def _save_gcs(file_content: bytes, content_type: str, recipe_id: str) -> Tuple[str, str]:
    bucket = _get_gcs_bucket()
    filename = uuid.uuid4().hex[:16]

    webp_bytes = _convert_to_webp(file_content)
    thumb_bytes = _make_thumbnail(file_content)

    image_path = f"{recipe_id}/{filename}.webp"
    thumb_path = f"{recipe_id}/{filename}_thumb.webp"

    for blob_path, data in [(image_path, webp_bytes), (thumb_path, thumb_bytes)]:
        blob = bucket.blob(blob_path)
        blob.upload_from_string(data, content_type="image/webp")
        blob.cache_control = "public, max-age=31536000"
        blob.patch()

    base_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}"
    image_url = f"{base_url}/{image_path}"
    thumbnail_url = f"{base_url}/{thumb_path}"
    return image_url, thumbnail_url


def _delete_gcs(image_url: str) -> bool:
    base_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/"
    if not image_url.startswith(base_url):
        return False

    blob_path = image_url.replace(base_url, "")
    bucket = _get_gcs_bucket()

    blob = bucket.blob(blob_path)
    if not blob.exists():
        return False
    blob.delete()

    # Also delete thumbnail
    base, ext = os.path.splitext(blob_path)
    thumb_blob = bucket.blob(f"{base}_thumb{ext}")
    if thumb_blob.exists():
        thumb_blob.delete()
    return True


# ── Public API (delegates based on STORAGE_MODE) ─────────────────

def save_image(file_content: bytes, content_type: str, recipe_id: str = "temp") -> Tuple[str, str]:
    """Save an uploaded image. Returns (image_url, thumbnail_url)."""
    _validate(file_content, content_type)

    if STORAGE_MODE == "gcs":
        return _save_gcs(file_content, content_type, recipe_id)
    return _save_local(file_content, content_type, recipe_id)


def delete_image(image_url: str) -> bool:
    """Delete an image by its URL."""
    if STORAGE_MODE == "gcs":
        return _delete_gcs(image_url)
    return _delete_local(image_url)
