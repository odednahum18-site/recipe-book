"""Tests for star/unstar functionality."""


def test_star_recipe(client, sample_recipe):
    """Visitor can star a recipe."""
    resp = client.post(f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    assert resp.status_code == 200
    assert resp.json()["star_count"] == 1


def test_duplicate_star(client, sample_recipe):
    """Starring twice doesn't double-count."""
    client.post(f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    resp = client.post(f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    assert resp.json()["star_count"] == 1
    assert "Already" in resp.json()["message"]


def test_unstar_recipe(client, sample_recipe):
    """Visitor can unstar a recipe."""
    client.post(f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    resp = client.request("DELETE", f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    assert resp.status_code == 200
    assert resp.json()["star_count"] == 0


def test_check_starred(client, sample_recipe):
    """Check if recipe is starred by visitor."""
    resp = client.get(f"/api/recipes/{sample_recipe['id']}/starred?visitor_id=visitor1")
    assert resp.json()["starred"] is False

    client.post(f"/api/recipes/{sample_recipe['id']}/star", json={"visitor_id": "visitor1"})
    resp = client.get(f"/api/recipes/{sample_recipe['id']}/starred?visitor_id=visitor1")
    assert resp.json()["starred"] is True
