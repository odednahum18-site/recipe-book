"""Auth routes: login, google-login, firebase-login, /me."""
import logging

from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import GOOGLE_CLIENT_ID
from models.schemas import LoginRequest, GoogleLoginRequest
from utils.repository import db
from utils.auth import create_access_token, require_editor, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, req: LoginRequest):
    user = db.get_by_field("users", "username", req.username)
    if not user or not verify_password(req.password, user.get("password", "")):
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


@router.post("/firebase-login")
async def firebase_login(user: dict = Depends(require_editor)):
    """Verify Firebase token and return user info. Used in production mode."""
    db_user = db.get_by_field("users", "email", user.get("email", ""))
    if db_user:
        return {"user": {
            "id": db_user["id"],
            "role": db_user.get("role", "editor"),
            "display_name": db_user.get("display_name", ""),
            "email": db_user.get("email", ""),
        }}
    raise HTTPException(status_code=403, detail="User not authorized. Ask an admin to invite you.")


@router.post("/google-login")
@limiter.limit("5/minute")
async def google_login(request: Request, req: GoogleLoginRequest):
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

    db_user = db.get_by_field("users", "email", email)
    if not db_user:
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
    return {"access_token": token, "token_type": "bearer", "user": {
        "id": db_user["id"],
        "role": db_user.get("role", "editor"),
        "display_name": db_user.get("display_name", ""),
        "email": email,
    }}


@router.get("/me")
async def get_me(user: dict = Depends(require_editor)):
    return {"id": user.get("sub"), "role": user.get("role"), "display_name": user.get("display_name")}
