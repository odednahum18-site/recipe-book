"""Tests for recipe CRUD and listing."""


def test_create_recipe(client, auth_header, sample_category):
    """Admin can create a recipe."""
    resp = client.post("/api/admin/recipes", json={
        "name": {"en": "Hummus", "he": "חומוס"},
        "category_ids": [sample_category["id"]],
        "ingredients": [{"text": {"en": "Chickpeas", "he": "חומוס"}, "amount": "2", "unit": {"en": "cups", "he": "כוסות"}}],
        "steps": {"en": "Blend", "he": "לטחון"},
        "published": True,
    }, headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"]["en"] == "Hummus"
    assert data["slug"] == "hummus"


def test_get_recipe_by_slug(client, auth_header, sample_recipe):
    """Public can get recipe by slug."""
    resp = client.get(f"/api/recipes/{sample_recipe['slug']}")
    assert resp.status_code == 200
    assert resp.json()["name"]["en"] == "Chocolate Cake"


def test_get_recipe_not_found(client):
    """Getting nonexistent recipe returns 404."""
    resp = client.get("/api/recipes/nonexistent-slug")
    assert resp.status_code == 404


def test_list_recipes_published_only(client, auth_header, sample_category):
    """Public listing only shows published recipes."""
    # Create published recipe
    client.post("/api/admin/recipes", json={
        "name": {"en": "Published", "he": "פורסם"},
        "category_ids": [sample_category["id"]],
        "ingredients": [{"text": {"en": "A", "he": "א"}, "amount": "1"}],
        "steps": {"en": "Do", "he": "עשה"},
        "published": True,
    }, headers=auth_header)
    # Create draft recipe
    client.post("/api/admin/recipes", json={
        "name": {"en": "Draft", "he": "טיוטא"},
        "category_ids": [sample_category["id"]],
        "ingredients": [{"text": {"en": "B", "he": "ב"}, "amount": "1"}],
        "steps": {"en": "Do", "he": "עשה"},
        "published": False,
    }, headers=auth_header)

    resp = client.get("/api/recipes")
    data = resp.json()
    assert data["total"] == 1
    assert data["data"][0]["name"]["en"] == "Published"


def test_list_recipes_filter_by_tag(client, auth_header, sample_recipe):
    """Filter recipes by dietary tag."""
    resp = client.get("/api/recipes?tag=parve")
    assert resp.json()["total"] == 1

    resp = client.get("/api/recipes?tag=meat")
    assert resp.json()["total"] == 0


def test_list_recipes_search(client, auth_header, sample_recipe):
    """Search recipes by name."""
    resp = client.get("/api/recipes?search=chocolate")
    assert resp.json()["total"] == 1

    resp = client.get("/api/recipes?search=pizza")
    assert resp.json()["total"] == 0


def test_update_recipe(client, auth_header, sample_recipe):
    """Admin can update a recipe."""
    resp = client.put(f"/api/admin/recipes/{sample_recipe['id']}", json={
        "name": {"en": "Updated Cake", "he": "עוגה מעודכנת"},
    }, headers=auth_header)
    assert resp.status_code == 200
    assert resp.json()["name"]["en"] == "Updated Cake"


def test_delete_recipe(client, auth_header, sample_recipe):
    """Admin can delete a recipe."""
    resp = client.delete(f"/api/admin/recipes/{sample_recipe['id']}", headers=auth_header)
    assert resp.status_code == 200

    resp = client.get(f"/api/recipes/{sample_recipe['slug']}")
    assert resp.status_code == 404
