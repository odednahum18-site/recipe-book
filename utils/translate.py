"""
Translation utilities using Google Cloud Translation API v2.
"""
import logging

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from google.cloud import translate_v2 as translate
        _client = translate.Client()
    return _client


def translate_batch(texts: list[dict], source_lang: str, target_lang: str) -> dict:
    """
    Translate multiple fields in one call.

    Args:
        texts: List of {"field": str, "value": str, "format": "text"|"html"}
        source_lang: Source language code ("en" or "he")
        target_lang: Target language code ("en" or "he")

    Returns:
        Dict mapping field names to translated strings.
    """
    results = {}
    # Separate text and html items, skip empty
    text_items = []
    html_items = []
    for item in texts:
        field = item["field"]
        value = item.get("value", "")
        if not value or not value.strip():
            results[field] = ""
            continue
        if item.get("format") == "html":
            html_items.append(item)
        else:
            text_items.append(item)

    client = _get_client()

    # Batch translate plain text items
    if text_items:
        values = [item["value"] for item in text_items]
        translated = client.translate(values, source_language=source_lang, target_language=target_lang, format_="text")
        for item, result in zip(text_items, translated):
            results[item["field"]] = result["translatedText"]

    # Batch translate HTML items
    if html_items:
        values = [item["value"] for item in html_items]
        translated = client.translate(values, source_language=source_lang, target_language=target_lang, format_="html")
        for item, result in zip(html_items, translated):
            results[item["field"]] = result["translatedText"]

    return results
