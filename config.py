"""
Configuration for Family Recipe Book
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server
PORT = int(os.getenv("PORT", 8080))
BASE_URL = os.getenv("BASE_URL", f"http://localhost:{PORT}")

# Environment mode: "local" or "production"
ENV_MODE = os.getenv("ENV_MODE", "local")

# Database mode: "json" (local dev) or "firestore" (production)
DB_MODE = os.getenv("DB_MODE", "json" if ENV_MODE == "local" else "firestore")

# Storage mode: "local" (local dev) or "gcs" (production)
STORAGE_MODE = os.getenv("STORAGE_MODE", "local" if ENV_MODE == "local" else "gcs")

# Auth mode: "jwt" (local dev) or "firebase" (production)
AUTH_MODE = os.getenv("AUTH_MODE", "jwt" if ENV_MODE == "local" else "firebase")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Auth (local dev - JWT)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 1440))  # 24 hours

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

# Google Cloud Storage
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "family-recipe-book-489413-recipe-images")

# Gemini (for OCR recipe parsing)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Image upload
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_RECIPE = 5
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
THUMBNAIL_WIDTH = 400
