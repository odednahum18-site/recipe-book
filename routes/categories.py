"""Public + admin category routes."""
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from models.schemas import CategoryCreate, CategoryOrderItem
from utils.repository import db
from utils.auth import require_editor, require_admin
from utils.helpers import slugify

router = APIRouter(tags=["categories"])


# ── Public ───────────────────────────────────────────────────────

@router.get("/api/categories")
async def list_categories():
    categories = db.get_all("categories")
    categories.sort(key=lambda c: c.get("order", 0))
    return categories


# ── Admin ────────────────────────────────────────────────────────

@router.post("/api/admin/categories")
async def create_category(cat: CategoryCreate, user: dict = Depends(require_editor)):
    slug = slugify(cat.name.en)
    data = {
        "slug": slug,
        "name": cat.name.model_dump(),
        "icon": cat.icon,
        "order": cat.order,
        "recipe_count": 0,
    }
    return db.create("categories", data)


@router.put("/api/admin/categories/reorder")
async def reorder_categories(order: List[CategoryOrderItem], user: dict = Depends(require_editor)):
    for item in order:
        db.update("categories", item.id, {"order": item.order})
    return {"message": "Reordered"}


@router.put("/api/admin/categories/{category_id}")
async def update_category(category_id: str, cat: CategoryCreate, user: dict = Depends(require_editor)):
    existing = db.get_by_id("categories", category_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")

    data = {
        "slug": slugify(cat.name.en),
        "name": cat.name.model_dump(),
        "icon": cat.icon,
        "order": cat.order,
    }
    return db.update("categories", category_id, data)


@router.delete("/api/admin/categories/{category_id}")
async def delete_category(category_id: str, user: dict = Depends(require_admin)):
    existing = db.get_by_id("categories", category_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    if existing.get("recipe_count", 0) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with recipes")

    db.delete("categories", category_id)
    return {"message": "Category deleted"}
