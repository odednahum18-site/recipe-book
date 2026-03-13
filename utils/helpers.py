"""Shared helper functions."""
import re
from utils.repository import db


def slugify(text: str) -> str:
    """Create URL-friendly slug from English text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def update_category_counts(category_ids: list[str]):
    """Recalculate recipe_count for multiple categories in a single pass."""
    if not category_ids:
        return
    recipes = db.query("recipes", {"published": True})
    counts = {cid: 0 for cid in category_ids}
    for r in recipes:
        for cid in r.get("category_ids", []):
            if cid in counts:
                counts[cid] += 1
    for cid, count in counts.items():
        db.update("categories", cid, {"recipe_count": count})


def star_id(recipe_id: str, visitor_id: str) -> str:
    """Build a deterministic star ID from recipe + visitor."""
    return f"{recipe_id}__{visitor_id}"
