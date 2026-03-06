"""
Authentication utility.
Local dev: JWT with credentials from .env
Production: Firebase Auth token verification
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, AUTH_MODE

security = HTTPBearer(auto_error=False)


# ── JWT auth (local dev) ─────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    from jose import jwt as jose_jwt
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jose_jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _verify_jwt(token: str) -> Optional[dict]:
    from jose import JWTError, jwt as jose_jwt
    try:
        payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# ── Firebase Auth (production) ───────────────────────────────────

_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        import firebase_admin
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        _firebase_initialized = True


def _verify_firebase_token(token: str) -> Optional[dict]:
    _init_firebase()
    from firebase_admin import auth as fb_auth
    try:
        decoded = fb_auth.verify_id_token(token)
        return {
            "sub": decoded["uid"],
            "email": decoded.get("email", ""),
            "role": decoded.get("role", "editor"),
            "display_name": decoded.get("name", decoded.get("email", "")),
        }
    except Exception:
        return None


# ── Unified interface ────────────────────────────────────────────

def verify_token(token: str) -> Optional[dict]:
    if AUTH_MODE == "firebase":
        return _verify_firebase_token(token)
    return _verify_jwt(token)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


async def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") not in ("admin", "editor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return user
