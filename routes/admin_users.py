"""Admin user management routes."""
from fastapi import APIRouter, HTTPException, Depends

from models.schemas import InviteRequest
from utils.repository import db
from utils.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin-users"])


@router.get("/users")
async def list_users(user: dict = Depends(require_admin)):
    users = db.get_all("users")
    return [
        {k: v for k, v in u.items() if k != "password"}
        for u in users
    ]


@router.post("/invite")
async def invite_user(req: InviteRequest, user: dict = Depends(require_admin)):
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


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_admin)):
    if user_id == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin user")
    if not db.delete("users", user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User removed"}
