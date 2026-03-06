"""
Configuration for Family Recipe Book
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server
PORT = int(os.getenv("PORT", 8080))
BASE_URL = os.getenv("BASE_URL", f"http://localhost:{PORT}")

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

# Image upload
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_RECIPE = 5
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
THUMBNAIL_WIDTH = 400
