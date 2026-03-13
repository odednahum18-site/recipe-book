"""Tests for category CRUD."""


def test_create_category(client, auth_header):
    """Admin can create a category."""
    resp = client.post("/api/admin/categories", json={
        "name": {"en": "Soups", "he": "מרקים"},
        "icon": "soup",
        "order": 5,
    }, headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["slug"] == "soups"


def test_list_categories(client, auth_header, sample_category):
    """Public can list categories."""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_update_category(client, auth_header, sample_category):
    """Admin can update a category."""
    resp = client.put(f"/api/admin/categories/{sample_category['id']}", json={
        "name": {"en": "Sweet Desserts", "he": "קינוחים מתוקים"},
        "icon": "cake",
        "order": 1,
    }, headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["name"]["en"] == "Sweet Desserts"


def test_delete_empty_category(client, auth_header):
    """Admin can delete a category with no recipes."""
    resp = client.post("/api/admin/categories", json={
        "name": {"en": "Empty", "he": "ריק"},
    }, headers=auth_header)
    cat_id = resp.json()["id"]

    resp = client.delete(f"/api/admin/categories/{cat_id}", headers=auth_header)
    assert resp.status_code == 200


def test_delete_category_with_recipes_fails(client, auth_header, sample_recipe, sample_category):
    """Cannot delete category that has recipes."""
    resp = client.delete(f"/api/admin/categories/{sample_category['id']}", headers=auth_header)
    assert resp.status_code == 400
    assert "recipes" in resp.json()["detail"].lower()
