"""Admin recipe CRUD and image upload routes."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query

from config import MAX_IMAGE_SIZE, ALLOWED_IMAGE_TYPES
from models.schemas import RecipeCreate, RecipeUpdate
from utils.repository import db
from utils.auth import require_editor
from utils.storage import save_image, delete_image
from utils.helpers import slugify, update_category_counts

router = APIRouter(prefix="/api/admin", tags=["admin-recipes"])


@router.get("/recipes")
async def admin_list_recipes(user: dict = Depends(require_editor)):
    recipes = db.get_all("recipes")
    recipes.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return recipes


@router.get("/recipes/{recipe_id}")
async def admin_get_recipe(recipe_id: str, user: dict = Depends(require_editor)):
    recipe = db.get_by_id("recipes", recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/recipes")
async def create_recipe(recipe: RecipeCreate, user: dict = Depends(require_editor)):
    slug = slugify(recipe.name.en)

    existing = db.get_by_field("recipes", "slug", slug)
    if existing:
        slug = f"{slug}-{db.count('recipes') + 1}"

    data = {
        "slug": slug,
        "name": recipe.name.model_dump(),
        "recipe_of": recipe.recipe_of.model_dump() if recipe.recipe_of else None,
        "category_ids": recipe.category_ids,
        "tags": recipe.tags or [],
        "ingredients": [i.model_dump() for i in recipe.ingredients],
        "steps": recipe.steps.model_dump(),
        "images": recipe.images or [],
        "star_count": 0,
        "published": recipe.published,
        "prep_time": recipe.prep_time,
        "difficulty": recipe.difficulty,
        "servings": recipe.servings,
        "created_by": user.get("sub", "unknown"),
    }
    created = db.create("recipes", data)

    if recipe.published:
        update_category_counts(recipe.category_ids)

    return created


@router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: RecipeUpdate, user: dict = Depends(require_editor)):
    existing = db.get_by_id("recipes", recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = {}
    if recipe.name is not None:
        update_data["name"] = recipe.name.model_dump()
        update_data["slug"] = slugify(recipe.name.en)
    if recipe.recipe_of is not None:
        update_data["recipe_of"] = recipe.recipe_of.model_dump()
    if recipe.category_ids is not None:
        update_data["category_ids"] = recipe.category_ids
    if recipe.tags is not None:
        update_data["tags"] = recipe.tags
    if recipe.ingredients is not None:
        update_data["ingredients"] = [i.model_dump() for i in recipe.ingredients]
    if recipe.steps is not None:
        update_data["steps"] = recipe.steps.model_dump()
    if recipe.images is not None:
        update_data["images"] = recipe.images
    if recipe.published is not None:
        update_data["published"] = recipe.published
    if recipe.prep_time is not None:
        update_data["prep_time"] = recipe.prep_time
    if recipe.difficulty is not None:
        update_data["difficulty"] = recipe.difficulty
    if recipe.servings is not None:
        update_data["servings"] = recipe.servings

    updated = db.update("recipes", recipe_id, update_data)

    old_cats = set(existing.get("category_ids", []))
    new_cats = set(update_data.get("category_ids", old_cats))
    pub_changed = "published" in update_data and update_data["published"] != existing.get("published")
    cats_changed = new_cats != old_cats
    if pub_changed or cats_changed:
        update_category_counts(list(old_cats | new_cats))

    return updated


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str, user: dict = Depends(require_editor)):
    existing = db.get_by_id("recipes", recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for img in existing.get("images", []):
        delete_image(img.get("url", ""))

    db.delete("recipes", recipe_id)
    update_category_counts(existing.get("category_ids", []))
    return {"message": "Recipe deleted"}


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    recipe_id: str = Query("temp"),
    user: dict = Depends(require_editor),
):
    content = await file.read()

    try:
        image_url, thumbnail_url = save_image(content, file.content_type, recipe_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"url": image_url, "thumbnail_url": thumbnail_url}
