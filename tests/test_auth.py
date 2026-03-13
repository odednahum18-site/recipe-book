"""Tests for authentication endpoints."""


def test_login_valid_credentials(client, admin_token):
    """Login with valid credentials returns token."""
    assert admin_token is not None


def test_login_invalid_password(client):
    """Login with wrong password returns 401."""
    from utils.repository import db
    from utils.auth import hash_password
    db.create("users", {
        "id": "admin",
        "username": "admin",
        "password": hash_password("correct"),
        "role": "admin",
    })
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    """Login with unknown user returns 401."""
    resp = client.post("/api/auth/login", json={"username": "nobody", "password": "pass"})
    assert resp.status_code == 401


def test_me_with_valid_token(client, admin_token):
    """GET /me with valid token returns user info."""
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"


def test_me_without_token(client):
    """GET /me without token returns 401."""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_invalid_token(client):
    """GET /me with garbage token returns 401."""
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


def test_admin_can_access_admin_endpoints(client, auth_header, sample_category):
    """Admin role can access admin endpoints."""
    resp = client.get("/api/admin/recipes", headers=auth_header)
    assert resp.status_code == 200


def test_editor_can_access_recipe_endpoints(client, editor_header):
    """Editor role can access recipe management endpoints."""
    resp = client.get("/api/admin/recipes", headers=editor_header)
    assert resp.status_code == 200


def test_editor_cannot_access_user_management(client, editor_header):
    """Editor role cannot access user management (require_admin)."""
    resp = client.get("/api/admin/users", headers=editor_header)
    assert resp.status_code == 403


def test_editor_cannot_invite_users(client, editor_header):
    """Editor cannot invite new users."""
    resp = client.post("/api/admin/invite", json={
        "email": "new@test.com",
    }, headers=editor_header)
    assert resp.status_code == 403
