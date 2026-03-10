"""
OCR utilities: Google Cloud Vision for text extraction + Gemini for structured parsing.
"""
import html as html_module
import json
import logging

from config import GEMINI_MODEL

logger = logging.getLogger(__name__)

_vision_client = None
_genai_client = None


def _get_vision_client():
    global _vision_client
    if _vision_client is None:
        from google.cloud import vision
        _vision_client = vision.ImageAnnotatorClient()
    return _vision_client


def _get_genai_client():
    global _genai_client
    if _genai_client is None:
        from google import genai
        _genai_client = genai.Client()
    return _genai_client


def _extract_text(image_bytes: bytes) -> tuple[str, str]:
    """
    Extract text from image using Vision API.
    Returns (raw_text, detected_language).
    """
    from google.cloud import vision

    client = _get_vision_client()
    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise ValueError(f"Vision API error: {response.error.message}")

    if not response.full_text_annotation.text:
        raise ValueError("No text detected in the image. Please try a clearer photo.")

    raw_text = response.full_text_annotation.text

    # Detect language from first page
    detected_lang = "he"  # default to Hebrew for a family recipe book
    try:
        pages = response.full_text_annotation.pages
        if pages:
            detected_languages = pages[0].property.detected_languages
            if detected_languages:
                lang_code = detected_languages[0].language_code
                detected_lang = "en" if lang_code.startswith("en") else "he"
    except Exception:
        pass

    logger.info(f"OCR extracted {len(raw_text)} chars, detected language: {detected_lang}")
    return raw_text, detected_lang


def _parse_with_gemini(raw_text: str, detected_lang: str) -> dict:
    """
    Use Gemini to parse raw OCR text into structured recipe fields.
    """
    lang_name = "Hebrew" if detected_lang == "he" else "English"

    prompt = f"""You are a recipe parser. Given OCR text from a recipe photo, extract structured data.

The text is in {lang_name}.

Return ONLY valid JSON with this exact structure:
{{
  "name": "recipe name as a string",
  "ingredients": [
    {{"text": "ingredient name", "amount": "2", "unit": "cups"}},
    ...
  ],
  "steps": "Step 1: ... Step 2: ..."
}}

Rules:
- Separate amount and unit from ingredient text (e.g., "2 cups flour" -> amount: "2", unit: "cups", text: "flour")
- For Hebrew units, use Hebrew text (e.g., "כוסות", "כפות")
- Steps should be formatted as HTML with <ol><li> tags for numbered steps
- If you cannot identify a section, leave it as empty string
- Do not invent or add content that is not in the OCR text
- Return ONLY the JSON, no markdown code fences

OCR Text:
{raw_text}"""

    client = _get_genai_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    response_text = response.text.strip()
    # Strip markdown code fences if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last line (``` markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)


def scan_recipe_image(image_bytes: bytes) -> dict:
    """
    Full pipeline: OCR image -> parse with Gemini -> return structured recipe data.

    Returns:
        {
            "detected_language": "he" | "en",
            "name": "recipe name",
            "ingredients": [{"text": "...", "amount": "...", "unit": "..."}],
            "steps": "HTML formatted steps"
        }
    """
    raw_text, detected_lang = _extract_text(image_bytes)

    try:
        parsed = _parse_with_gemini(raw_text, detected_lang)
    except Exception as e:
        logger.warning(f"Gemini parsing failed: {e}. Falling back to raw text.")
        # Fallback: put raw text in steps
        return {
            "detected_language": detected_lang,
            "name": "",
            "ingredients": [],
            "steps": f"<p>{html_module.escape(raw_text)}</p>",
        }

    return {
        "detected_language": detected_lang,
        "name": parsed.get("name", ""),
        "ingredients": parsed.get("ingredients", []),
        "steps": parsed.get("steps", ""),
    }
