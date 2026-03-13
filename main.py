"""
Family Recipe Book - FastAPI Application

Bilingual (Hebrew/English) recipe management with admin auth,
image uploads, star ratings, and category navigation.

Port: 8080
"""
import os
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from config import PORT, STATIC_DIR, UPLOADS_DIR, STORAGE_MODE, ENV_MODE, JWT_SECRET, ADMIN_PASSWORD
from utils.repository import db
from utils.auth import hash_password
from utils.seed_data import seed_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ── Migrations ──────────────────────────────────────────────────

def _migrate_category_id_to_ids():
    """Migrate recipes from category_id (string) to category_ids (list)."""
    recipes = db.get_all("recipes")
    migrated = 0
    for recipe in recipes:
        if "category_id" in recipe and "category_ids" not in recipe:
            cat_id = recipe["category_id"]
            db.update("recipes", recipe["id"], {
                "category_ids": [cat_id] if cat_id else [],
            })
            migrated += 1
    if migrated:
        logger.info(f"Migrated {migrated} recipes from category_id to category_ids")


def _migrate_plaintext_passwords():
    """One-time migration: hash any plaintext passwords in the users collection."""
    users = db.get_all("users")
    migrated = 0
    for user in users:
        pw = user.get("password", "")
        if pw and not pw.startswith("$2b$"):
            db.update("users", user["id"], {"password": hash_password(pw)})
            migrated += 1
    if migrated:
        logger.info(f"Migrated {migrated} user password(s) to bcrypt")


# ── Lifespan ────────────────────────────────────────────────────

_index_html_cache: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _index_html_cache

    # Validate required config in production
    if ENV_MODE != "local":
        if not JWT_SECRET:
            raise RuntimeError("JWT_SECRET environment variable is required in production")
        if not ADMIN_PASSWORD:
            raise RuntimeError("ADMIN_PASSWORD environment variable is required in production")

    # Seed data and run migrations
    if ENV_MODE != "production":
        result = seed_all()
        if result["categories_seeded"]:
            logger.info("Seeded initial categories")
        if result["admin_seeded"]:
            logger.info("Seeded admin user")
    else:
        # In production, only seed categories (not admin user) if needed
        from utils.seed_data import seed_categories
        if seed_categories():
            logger.info("Seeded initial categories")

    _migrate_category_id_to_ids()
    _migrate_plaintext_passwords()

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


# ── FastAPI App ─────────────────────────────────────────────────

app = FastAPI(title="Family Recipe Book", version="1.0.0", lifespan=lifespan)

# CORS
_allowed_origins = (
    ["https://recipe-book-5855517854.me-west1.run.app"]
    if ENV_MODE == "production"
    else ["http://localhost:5173", "http://localhost:8080"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Register Routers ────────────────────────────────────────────

from routes.auth import router as auth_router
from routes.recipes import router as recipes_router
from routes.categories import router as categories_router
from routes.stars import router as stars_router
from routes.admin_recipes import router as admin_recipes_router
from routes.admin_users import router as admin_users_router
from routes.admin_tools import router as admin_tools_router

app.include_router(auth_router)
app.include_router(recipes_router)
app.include_router(categories_router)
app.include_router(stars_router)
app.include_router(admin_recipes_router)
app.include_router(admin_users_router)
app.include_router(admin_tools_router)


# ── Health ──────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "app": "recipe-book"}


# ── Static Files & SPA ─────────────────────────────────────────

if STORAGE_MODE == "local":
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

ASSETS_DIR = os.path.join(STATIC_DIR, "assets")
if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


# SPA catch-all (must be LAST)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_spa(path: str = ""):
    if path.startswith("api/") or path.startswith("assets/") or path.startswith("uploads/") or path == "health":
        raise HTTPException(status_code=404)

    if _index_html_cache:
        return HTMLResponse(content=_index_html_cache)
    return HTMLResponse(
        content="<h1>Recipe Book</h1><p>Frontend not built yet. Run: cd frontend && npm run build</p>"
    )


# ── Run ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
