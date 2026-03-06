"""
Seed initial data into Firestore.
Run once after first deployment:
  gcloud run jobs execute seed-data --region me-west1
Or locally with GOOGLE_APPLICATION_CREDENTIALS set:
  DB_MODE=firestore python -m utils.seed_firestore
"""
from utils.firestore_repository import FirestoreRepository

INITIAL_CATEGORIES = [
    {"id": "appetizers", "slug": "appetizers", "name": {"en": "Appetizers", "he": "\u05de\u05e0\u05d5\u05ea \u05e8\u05d0\u05e9\u05d5\u05e0\u05d5\u05ea"}, "icon": "soup", "order": 1, "recipe_count": 0},
    {"id": "main-courses", "slug": "main-courses", "name": {"en": "Main Courses", "he": "\u05de\u05e0\u05d5\u05ea \u05e2\u05d9\u05e7\u05e8\u05d9\u05d5\u05ea"}, "icon": "dish", "order": 2, "recipe_count": 0},
    {"id": "desserts", "slug": "desserts", "name": {"en": "Desserts", "he": "\u05e7\u05d9\u05e0\u05d5\u05d7\u05d9\u05dd"}, "icon": "cake", "order": 3, "recipe_count": 0},
    {"id": "salads", "slug": "salads", "name": {"en": "Salads", "he": "\u05e1\u05dc\u05d8\u05d9\u05dd"}, "icon": "salad", "order": 4, "recipe_count": 0},
    {"id": "soups", "slug": "soups", "name": {"en": "Soups", "he": "\u05de\u05e8\u05e7\u05d9\u05dd"}, "icon": "soup", "order": 5, "recipe_count": 0},
    {"id": "beverages", "slug": "beverages", "name": {"en": "Beverages", "he": "\u05de\u05e9\u05e7\u05d0\u05d5\u05ea"}, "icon": "drink", "order": 6, "recipe_count": 0},
    {"id": "bread-pastry", "slug": "bread-pastry", "name": {"en": "Bread & Pastry", "he": "\u05dc\u05d7\u05dd \u05d5\u05de\u05d0\u05e4\u05d9\u05dd"}, "icon": "bread", "order": 7, "recipe_count": 0},
    {"id": "side-dishes", "slug": "side-dishes", "name": {"en": "Side Dishes", "he": "\u05ea\u05d5\u05e1\u05e4\u05d5\u05ea"}, "icon": "sides", "order": 8, "recipe_count": 0},
]


def seed_firestore():
    db = FirestoreRepository()

    # Seed categories
    existing = db.get_all("categories")
    if not existing:
        for cat in INITIAL_CATEGORIES:
            db.create("categories", dict(cat))
        print(f"Seeded {len(INITIAL_CATEGORIES)} categories")
    else:
        print(f"Categories already exist ({len(existing)} found), skipping")


if __name__ == "__main__":
    seed_firestore()
    print("Done!")
