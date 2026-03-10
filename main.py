"""
Family Recipe Book - FastAPI Application

Bilingual (Hebrew/English) recipe management with admin auth,
image uploads, star ratings, and category navigation.

Port: 8080
"""
import asyncio
import os
import re
import logging
from typing import Optional, List, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config import PORT, STATIC_DIR, UPLOADS_DIR, MAX_IMAGES_PER_RECIPE, MAX_IMAGE_SIZE, ALLOWED_IMAGE_TYPES, AUTH_MODE, STORAGE_MODE, GOOGLE_CLIENT_ID
from utils.repository import db
from utils.auth import create_access_token, get_admin_user
from utils.storage import save_image, delete_image
from utils.seed_data import seed_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ── Pydantic Models ─────────────────────────────────────────────

class BilingualText(BaseModel):
    en: str
    he: str


class IngredientInput(BaseModel):
    text: BilingualText
    amount: str
    unit: Optional[str] = ""


class RecipeCreate(BaseModel):
    name: BilingualText
    category_id: str
    ingredients: List[IngredientInput]
    steps: BilingualText
    images: Optional[List[dict]] = []
    published: Optional[bool] = False


class RecipeUpdate(BaseModel):
    name: Optional[BilingualText] = None
    category_id: Optional[str] = None
    ingredients: Optional[List[IngredientInput]] = None
    steps: Optional[BilingualText] = None
    images: Optional[List[dict]] = None
    published: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class StarRequest(BaseModel):
    visitor_id: str


class CategoryCreate(BaseModel):
    name: BilingualText
    icon: Optional[str] = ""
    order: Optional[int] = 0


class GoogleLoginRequest(BaseModel):
    credential: str


class InviteRequest(BaseModel):
    email: str
    display_name: Optional[str] = ""


class TranslateFieldItem(BaseModel):
    field: str
    value: str
    format: Literal["text", "html"] = "text"


class TranslateRequest(BaseModel):
    texts: List[TranslateFieldItem]
    source_lang: str
    target_lang: str


# ── Helpers ──────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Create URL-friendly slug from English text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _update_category_count(category_id: str):
    """Recalculate recipe_count for a category."""
    count = db.count("recipes", {"category_id": category_id, "published": True})
    db.update("categories", category_id, {"recipe_count": count})


def _star_id(recipe_id: str, visitor_id: str) -> str:
    """Build a deterministic star ID from recipe + visitor."""
    return f"{recipe_id}__{visitor_id}"


# ── Lifespan ─────────────────────────────────────────────────────

_index_html_cache: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _index_html_cache
    result = seed_all()
    if result["categories_seeded"]:
        logger.info("Seeded initial categories")
    if result["admin_seeded"]:
        logger.info("Seeded admin user")
    # Cache index.html for SPA serving
    index_path = os.path.join(STATIC_DIR, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            _index_html_cache = f.read()
    except FileNotFoundError:
        pass
    logger.info(f"Recipe Book started on port {PORT}")
    yield
    logger.info("Shutting down Recipe Book")


# ── FastAPI App ──────────────────────────────────────────────────

app = FastAPI(title="Family Recipe Book", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "app": "recipe-book"}


# ── Auth ─────────────────────────────────────────────────────────

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    from config import ADMIN_USERNAME, ADMIN_PASSWORD

    user = db.get_by_field("users", "username", req.username)
    if user and user.get("password") != req.password:
        user = None

    if user is None:
        # Check hardcoded admin as fallback
        if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
            user = {"id": "admin", "role": "admin", "display_name": "Admin"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user["id"],
        "role": user.get("role", "editor"),
        "display_name": user.get("display_name", ""),
    })
    return {"access_token": token, "token_type": "bearer", "user": {
        "id": user["id"],
        "role": user.get("role"),
        "display_name": user.get("display_name"),
    }}


@app.post("/api/auth/firebase-login")
async def firebase_login(user: dict = Depends(get_admin_user)):
    """Verify Firebase token and return user info. Used in production mode."""
    # Look up user in our DB to get role
    db_user = db.get_by_field("users", "email", user.get("email", ""))
    if db_user:
        return {"user": {
            "id": db_user["id"],
            "role": db_user.get("role", "editor"),
            "display_name": db_user.get("display_name", ""),
            "email": db_user.get("email", ""),
        }}
    raise HTTPException(status_code=403, detail="User not authorized. Ask an admin to invite you.")


@app.post("/api/auth/google-login")
async def google_login(req: GoogleLoginRequest):
    """Verify Google ID token and return JWT. User must be pre-invited by email."""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google login not configured")

    try:
        idinfo = id_token.verify_oauth2_token(
            req.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = idinfo.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="No email in Google token")

    logger.info(f"Google login attempt: email={email}")

    # Look up user by email — must be pre-invited
    db_user = db.get_by_field("users", "email", email)
    if not db_user:
        # Case-insensitive fallback: scan all users
        all_users = db.get_all("users")
        logger.info(f"Exact match failed. Users in DB: {[u.get('email') for u in all_users]}")
        for u in all_users:
            if u.get("email", "").strip().lower() == email:
                db_user = u
                break
    if not db_user:
        raise HTTPException(
            status_code=403,
            detail=f"Not authorized. Email '{email}' not found. Ask an admin to invite you."
        )

    token = create_access_token({
        "sub": db_user["id"],
        "role": db_user.get("role", "editor"),
        "display_name": db_user.get("display_name", idinfo.get("name", "")),
    })
    user_data = {
        "id": db_user["id"],
        "role": db_user.get("role", "editor"),
        "display_name": db_user.get("display_name", ""),
        "email": email,
    }
    return {"access_token": token, "token_type": "bearer", "user": user_data}


@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_admin_user)):
    return {"id": user.get("sub"), "role": user.get("role"), "display_name": user.get("display_name")}


# ── Public: Categories ───────────────────────────────────────────

@app.get("/api/categories")
async def list_categories():
    categories = db.get_all("categories")
    categories.sort(key=lambda c: c.get("order", 0))
    return categories


# ── Public: Recipes ──────────────────────────────────────────────

@app.get("/api/recipes")
async def list_recipes(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort: Optional[str] = Query("newest", description="Sort: newest, stars, name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    recipes = db.query("recipes", {"published": True})

    # Filter by category
    if category:
        cat = db.get_by_field("categories", "slug", category)
        if cat:
            recipes = [r for r in recipes if r.get("category_id") == cat["id"]]

    # Search by name
    if search:
        search_lower = search.lower()
        recipes = [
            r for r in recipes
            if search_lower in r.get("name", {}).get("en", "").lower()
            or search_lower in r.get("name", {}).get("he", "")
        ]

    # Sort
    if sort == "stars":
        recipes.sort(key=lambda r: r.get("star_count", 0), reverse=True)
    elif sort == "name":
        recipes.sort(key=lambda r: r.get("name", {}).get("en", "").lower())
    else:  # newest
        recipes.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    # Paginate
    total = len(recipes)
    start = (page - 1) * page_size
    recipes = recipes[start : start + page_size]

    return {"data": recipes, "total": total, "page": page, "page_size": page_size}


@app.get("/api/recipes/{slug}")
async def get_recipe(slug: str):
    recipe = db.get_by_field("recipes", "slug", slug)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


# ── Public: Stars ────────────────────────────────────────────────

@app.post("/api/recipes/{recipe_id}/star")
async def star_recipe(recipe_id: str, req: StarRequest):
    recipe = db.get_by_id("recipes", recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    sid = _star_id(recipe_id, req.visitor_id)
    existing = db.get_by_id("stars", sid)
    if existing:
        return {"message": "Already starred", "star_count": recipe.get("star_count", 0)}

    db.create("stars", {"id": sid, "recipe_id": recipe_id, "visitor_id": req.visitor_id})
    new_count = recipe.get("star_count", 0) + 1
    db.update("recipes", recipe_id, {"star_count": new_count})
    return {"message": "Starred", "star_count": new_count}


@app.delete("/api/recipes/{recipe_id}/star")
async def unstar_recipe(recipe_id: str, req: StarRequest):
    recipe = db.get_by_id("recipes", recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    sid = _star_id(recipe_id, req.visitor_id)
    deleted = db.delete("stars", sid)
    if not deleted:
        return {"message": "Not starred", "star_count": recipe.get("star_count", 0)}

    new_count = max(0, recipe.get("star_count", 0) - 1)
    db.update("recipes", recipe_id, {"star_count": new_count})
    return {"message": "Unstarred", "star_count": new_count}


@app.get("/api/recipes/{recipe_id}/starred")
async def check_starred(recipe_id: str, visitor_id: str = Query(...)):
    sid = _star_id(recipe_id, visitor_id)
    existing = db.get_by_id("stars", sid)
    return {"starred": existing is not None}


# ── Admin: Recipes ───────────────────────────────────────────────

@app.get("/api/admin/recipes")
async def admin_list_recipes(user: dict = Depends(get_admin_user)):
    recipes = db.get_all("recipes")
    recipes.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return recipes


@app.post("/api/admin/recipes")
async def create_recipe(recipe: RecipeCreate, user: dict = Depends(get_admin_user)):
    slug = _slugify(recipe.name.en)

    # Ensure unique slug
    existing = db.get_by_field("recipes", "slug", slug)
    if existing:
        slug = f"{slug}-{db.count('recipes') + 1}"

    data = {
        "slug": slug,
        "name": recipe.name.model_dump(),
        "category_id": recipe.category_id,
        "ingredients": [i.model_dump() for i in recipe.ingredients],
        "steps": recipe.steps.model_dump(),
        "images": recipe.images or [],
        "star_count": 0,
        "published": recipe.published,
        "created_by": user.get("sub", "unknown"),
    }
    created = db.create("recipes", data)

    if recipe.published:
        _update_category_count(recipe.category_id)

    return created


@app.put("/api/admin/recipes/{recipe_id}")
async def update_recipe(recipe_id: str, recipe: RecipeUpdate, user: dict = Depends(get_admin_user)):
    existing = db.get_by_id("recipes", recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = {}
    if recipe.name is not None:
        update_data["name"] = recipe.name.model_dump()
        update_data["slug"] = _slugify(recipe.name.en)
    if recipe.category_id is not None:
        update_data["category_id"] = recipe.category_id
    if recipe.ingredients is not None:
        update_data["ingredients"] = [i.model_dump() for i in recipe.ingredients]
    if recipe.steps is not None:
        update_data["steps"] = recipe.steps.model_dump()
    if recipe.images is not None:
        update_data["images"] = recipe.images
    if recipe.published is not None:
        update_data["published"] = recipe.published

    updated = db.update("recipes", recipe_id, update_data)

    # Update category counts only if category or published status changed
    old_cat = existing.get("category_id")
    new_cat = update_data.get("category_id", old_cat)
    pub_changed = "published" in update_data and update_data["published"] != existing.get("published")
    cat_changed = new_cat != old_cat
    if pub_changed or cat_changed:
        _update_category_count(old_cat)
        if cat_changed:
            _update_category_count(new_cat)

    return updated


@app.delete("/api/admin/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str, user: dict = Depends(get_admin_user)):
    existing = db.get_by_id("recipes", recipe_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Delete associated images
    for img in existing.get("images", []):
        delete_image(img.get("url", ""))

    db.delete("recipes", recipe_id)
    _update_category_count(existing.get("category_id", ""))
    return {"message": "Recipe deleted"}


# ── Admin: Image Upload ─────────────────────────────────────────

@app.post("/api/admin/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    recipe_id: str = Query("temp"),
    user: dict = Depends(get_admin_user),
):
    content = await file.read()

    try:
        image_url, thumbnail_url = save_image(content, file.content_type, recipe_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"url": image_url, "thumbnail_url": thumbnail_url}


# ── Admin: Categories ────────────────────────────────────────────

@app.post("/api/admin/categories")
async def create_category(cat: CategoryCreate, user: dict = Depends(get_admin_user)):
    slug = _slugify(cat.name.en)
    data = {
        "slug": slug,
        "name": cat.name.model_dump(),
        "icon": cat.icon,
        "order": cat.order,
        "recipe_count": 0,
    }
    return db.create("categories", data)


@app.put("/api/admin/categories/{category_id}")
async def update_category(category_id: str, cat: CategoryCreate, user: dict = Depends(get_admin_user)):
    existing = db.get_by_id("categories", category_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")

    data = {
        "slug": _slugify(cat.name.en),
        "name": cat.name.model_dump(),
        "icon": cat.icon,
        "order": cat.order,
    }
    return db.update("categories", category_id, data)


@app.delete("/api/admin/categories/{category_id}")
async def delete_category(category_id: str, user: dict = Depends(get_admin_user)):
    recipes = db.query("recipes", {"category_id": category_id})
    if recipes:
        raise HTTPException(status_code=400, detail="Cannot delete category with recipes")

    if not db.delete("categories", category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}


# ── Admin: User Management ──────────────────────────────────────

@app.get("/api/admin/users")
async def list_users(user: dict = Depends(get_admin_user)):
    users = db.get_all("users")
    # Don't expose passwords
    return [
        {k: v for k, v in u.items() if k != "password"}
        for u in users
    ]


@app.post("/api/admin/invite")
async def invite_user(req: InviteRequest, user: dict = Depends(get_admin_user)):
    invite_email = req.email.strip().lower()
    if db.exists("users", "email", invite_email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = db.create("users", {
        "email": invite_email,
        "display_name": req.display_name or invite_email.split("@")[0],
        "role": "editor",
        "invited_by": user.get("sub"),
    })
    return new_user


@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(get_admin_user)):
    if user_id == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin user")
    if not db.delete("users", user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User removed"}


# ── Admin: Scan Recipe (OCR) ────────────────────────────────────

@app.post("/api/admin/scan-recipe")
async def scan_recipe(
    file: UploadFile = File(...),
    user: dict = Depends(get_admin_user),
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


# ── Admin: Translate ────────────────────────────────────────────

@app.post("/api/admin/translate")
async def translate_recipe_fields(req: TranslateRequest, user: dict = Depends(get_admin_user)):
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


# ── Static Files & SPA ───────────────────────────────────────────

# Serve uploaded images locally (GCS mode serves directly from bucket)
if STORAGE_MODE == "local":
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Serve built frontend assets
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


# SPA catch-all
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_spa(path: str = ""):
    if path.startswith("api/") or path.startswith("assets/") or path.startswith("uploads/") or path == "health":
        raise HTTPException(status_code=404)

    if _index_html_cache:
        return HTMLResponse(content=_index_html_cache)
    return HTMLResponse(
        content="<h1>Recipe Book</h1><p>Frontend not built yet. Run: cd frontend && npm run build</p>"
    )


# ── Run ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
