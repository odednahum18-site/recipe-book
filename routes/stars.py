"""Star/unstar routes."""
from fastapi import APIRouter, HTTPException, Query

from models.schemas import StarRequest
from utils.repository import db
from utils.helpers import star_id

router = APIRouter(prefix="/api/recipes", tags=["stars"])


@router.post("/{recipe_id}/star")
async def star_recipe(recipe_id: str, req: StarRequest):
    recipe = db.get_by_id("recipes", recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    sid = star_id(recipe_id, req.visitor_id)
    existing = db.get_by_id("stars", sid)
    if existing:
        return {"message": "Already starred", "star_count": recipe.get("star_count", 0)}

    db.create("stars", {"id": sid, "recipe_id": recipe_id, "visitor_id": req.visitor_id})
    new_count = recipe.get("star_count", 0) + 1
    db.update("recipes", recipe_id, {"star_count": new_count})
    return {"message": "Starred", "star_count": new_count}


@router.delete("/{recipe_id}/star")
async def unstar_recipe(recipe_id: str, req: StarRequest):
    recipe = db.get_by_id("recipes", recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    sid = star_id(recipe_id, req.visitor_id)
    deleted = db.delete("stars", sid)
    if not deleted:
        return {"message": "Not starred", "star_count": recipe.get("star_count", 0)}

    new_count = max(0, recipe.get("star_count", 0) - 1)
    db.update("recipes", recipe_id, {"star_count": new_count})
    return {"message": "Unstarred", "star_count": new_count}


@router.get("/{recipe_id}/starred")
async def check_starred(recipe_id: str, visitor_id: str = Query(...)):
    sid = star_id(recipe_id, visitor_id)
    existing = db.get_by_id("stars", sid)
    return {"starred": existing is not None}
