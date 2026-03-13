"""
Seed initial categories and admin user.
"""
from utils.repository import db
from utils.auth import hash_password
from config import ADMIN_USERNAME, ADMIN_PASSWORD

INITIAL_CATEGORIES = [
    {"slug": "appetizers", "name": {"en": "Appetizers", "he": "\u05de\u05e0\u05d5\u05ea \u05e8\u05d0\u05e9\u05d5\u05e0\u05d5\u05ea"}, "icon": "soup", "order": 1},
    {"slug": "main-courses", "name": {"en": "Main Courses", "he": "\u05de\u05e0\u05d5\u05ea \u05e2\u05d9\u05e7\u05e8\u05d9\u05d5\u05ea"}, "icon": "dish", "order": 2},
    {"slug": "desserts", "name": {"en": "Desserts", "he": "\u05e7\u05d9\u05e0\u05d5\u05d7\u05d9\u05dd"}, "icon": "cake", "order": 3},
    {"slug": "salads", "name": {"en": "Salads", "he": "\u05e1\u05dc\u05d8\u05d9\u05dd"}, "icon": "salad", "order": 4},
    {"slug": "soups", "name": {"en": "Soups", "he": "\u05de\u05e8\u05e7\u05d9\u05dd"}, "icon": "soup", "order": 5},
    {"slug": "bread-pastry", "name": {"en": "Bread & Pastry", "he": "\u05dc\u05d7\u05dd \u05d5\u05de\u05d0\u05e4\u05d9\u05dd"}, "icon": "bread", "order": 6},
    {"slug": "side-dishes", "name": {"en": "Side Dishes", "he": "\u05ea\u05d5\u05e1\u05e4\u05d5\u05ea"}, "icon": "sides", "order": 7},
]


def seed_categories():
    """Seed categories if none exist."""
    existing = db.get_all("categories")
    if existing:
        return False

    for cat in INITIAL_CATEGORIES:
        cat_copy = dict(cat)
        cat_copy["recipe_count"] = 0
        db.create("categories", cat_copy)
    return True


def seed_admin_user():
    """Seed admin user if none exist."""
    existing = db.get_all("users")
    if existing:
        return False

    db.create("users", {
        "id": "admin",
        "email": f"{ADMIN_USERNAME}@localhost",
        "display_name": "Admin",
        "role": "admin",
        "username": ADMIN_USERNAME,
        "password": hash_password(ADMIN_PASSWORD) if ADMIN_PASSWORD else "",
        "invited_by": None,
    })
    return True


def seed_all():
    """Run all seed functions."""
    cats = seed_categories()
    user = seed_admin_user()
    return {"categories_seeded": cats, "admin_seeded": user}
