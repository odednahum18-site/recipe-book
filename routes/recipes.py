"""Public recipe routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from models.schemas import DIETARY_TAGS
from utils.repository import db

router = APIRouter(prefix="/api", tags=["recipes"])


@router.get("/tags")
async def list_tags():
    return DIETARY_TAGS


@router.get("/recipes")
async def list_recipes(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort: Optional[str] = Query("newest", description="Sort: newest, stars, name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    # Resolve category slug to ID
    category_id = None
    if category:
        cat = db.get_by_field("categories", "slug", category)
        if cat:
            category_id = cat["id"]

    offset = (page - 1) * page_size
    recipes, total = db.query_recipes(
        category_id=category_id,
        tag=tag,
        search=search,
        sort_by=sort,
        offset=offset,
        limit=page_size,
    )

    return {"data": recipes, "total": total, "page": page, "page_size": page_size}


@router.get("/recipes/{slug}")
async def get_recipe(slug: str):
    recipe = db.get_by_field("recipes", "slug", slug)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
