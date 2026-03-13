"""Admin tools: OCR scan and translate."""
import asyncio

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File

from config import MAX_IMAGE_SIZE, ALLOWED_IMAGE_TYPES
from models.schemas import TranslateRequest
from utils.auth import require_editor

router = APIRouter(prefix="/api/admin", tags=["admin-tools"])


@router.post("/scan-recipe")
async def scan_recipe(
    file: UploadFile = File(...),
    user: dict = Depends(require_editor),
):
    """Scan a recipe photo and return structured recipe data."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    from utils.ocr import scan_recipe_image
    try:
        result = await asyncio.to_thread(scan_recipe_image, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@router.post("/translate")
async def translate_recipe_fields(req: TranslateRequest, user: dict = Depends(require_editor)):
    """Batch translate recipe fields between Hebrew and English."""
    if req.source_lang not in ("en", "he") or req.target_lang not in ("en", "he"):
        raise HTTPException(status_code=400, detail="source_lang and target_lang must be 'en' or 'he'")

    from utils.translate import translate_batch
    items = [{"field": t.field, "value": t.value, "format": t.format} for t in req.texts]
    try:
        translations = await asyncio.to_thread(translate_batch, items, req.source_lang, req.target_lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    return {"translations": translations}
