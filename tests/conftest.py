"""Test fixtures for the Recipe Book application."""
import os
import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient

# Force local/test mode before importing app
os.environ["ENV_MODE"] = "local"
os.environ["DB_MODE"] = "json"
os.environ["STORAGE_MODE"] = "local"
os.environ["AUTH_MODE"] = "jwt"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "testpass123"
os.environ["JWT_SECRET"] = "test-secret-key"


@pytest.fixture(autouse=True)
def temp_data_dir(monkeypatch):
    """Use a temp directory for JSON data files per test."""
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr("config.DATA_DIR", tmpdir)
    # Also patch the repository's DATA_DIR
    import utils.repository as repo_mod
    if hasattr(repo_mod, 'db') and hasattr(repo_mod.db, '_file_path'):
        original_file_path = repo_mod.db._file_path
        monkeypatch.setattr(repo_mod.db, '_file_path',
                            lambda collection: os.path.join(tmpdir, f"{collection}.json"))
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def client():
    """FastAPI test client."""
    from main import app
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Get a valid admin JWT token."""
    from utils.repository import db
    from utils.auth import hash_password, create_access_token
    db.create("users", {
        "id": "admin",
        "username": "admin",
        "password": hash_password("testpass123"),
        "email": "admin@localhost",
        "display_name": "Admin",
        "role": "admin",
    })
    return create_access_token({"sub": "admin", "role": "admin", "display_name": "Admin"})


@pytest.fixture
def editor_token(client):
    """Get a valid editor JWT token."""
    from utils.repository import db
    from utils.auth import hash_password, create_access_token
    db.create("users", {
        "id": "editor1",
        "username": "editor1",
        "password": hash_password("editorpass"),
        "email": "editor@test.com",
        "display_name": "Editor",
        "role": "editor",
    })
    return create_access_token({"sub": "editor1", "role": "editor", "display_name": "Editor"})


@pytest.fixture
def auth_header(admin_token):
    """Authorization header with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def editor_header(editor_token):
    """Authorization header with editor token."""
    return {"Authorization": f"Bearer {editor_token}"}


@pytest.fixture
def sample_category(client, auth_header):
    """Create and return a sample category."""
    resp = client.post("/api/admin/categories", json={
        "name": {"en": "Desserts", "he": "קינוחים"},
        "icon": "cake",
        "order": 1,
    }, headers=auth_header)
    return resp.json()


@pytest.fixture
def sample_recipe(client, auth_header, sample_category):
    """Create and return a sample published recipe."""
    resp = client.post("/api/admin/recipes", json={
        "name": {"en": "Chocolate Cake", "he": "עוגת שוקולד"},
        "category_ids": [sample_category["id"]],
        "tags": ["parve"],
        "ingredients": [{"text": {"en": "Flour", "he": "קמח"}, "amount": "2", "unit": {"en": "cups", "he": "כוסות"}}],
        "steps": {"en": "Mix and bake", "he": "לערבב ולאפות"},
        "published": True,
    }, headers=auth_header)
    return resp.json()
