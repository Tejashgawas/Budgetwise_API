import pytest
from app.models.category import Category
from app.extensions import db

# ---------------------------
# HELPER: Seed Category
# ---------------------------
def seed_category(user_id=1, name="Food", type="expense"):
    cat = Category(name=name, type=type, user_id=user_id)
    db.session.add(cat)
    db.session.commit()
    return cat

# ---------------------------
# CREATE CATEGORY
# ---------------------------
def test_create_category_route(client, auth_header):
    payload = {"name": "Food", "type": "expense"}
    res = client.post("/api/categories/", json=payload, headers=auth_header)
    assert res.status_code == 201
    data = res.json
    assert data["category"]["name"] == "Food"
    assert data["category"]["type"] == "expense"

def test_create_category_validation_error(client, auth_header):
    payload = {"name": "F"}  # invalid, missing type
    res = client.post("/api/categories/", json=payload, headers=auth_header)
    assert res.status_code == 400
    assert "errors" in res.json

# ---------------------------
# GET ALL CATEGORIES
# ---------------------------
def test_get_all_categories_route(client, auth_header):
    cat = seed_category(name="Travel")
    res = client.get("/api/categories/", headers=auth_header)
    assert res.status_code == 200
    data = res.json
    assert any(c["name"] == "Travel" for c in data)

# ---------------------------
# GET CATEGORY BY ID
# ---------------------------
def test_get_category_by_id_route(client, auth_header):
    cat = seed_category(name="Books")
    res = client.get(f"/api/categories/{cat.id}", headers=auth_header)
    assert res.status_code == 200
    data = res.json
    assert data["id"] == cat.id
    assert data["name"] == "Books"

def test_get_category_not_found_route(client, auth_header):
    res = client.get("/api/categories/9999", headers=auth_header)
    assert res.status_code == 400 or res.status_code == 404  # depends on your error handling

# ---------------------------
# UPDATE CATEGORY
# ---------------------------
def test_update_category_route(client, auth_header):
    cat = seed_category(name="OldName")
    payload = {"name": "NewName", "type": "income"}
    res = client.put(f"/api/categories/{cat.id}", json=payload, headers=auth_header)
    assert res.status_code == 200
    data = res.json
    assert data["category"]["name"] == "NewName"
    assert data["category"]["type"] == "income"

# ---------------------------
# DELETE CATEGORY
# ---------------------------
def test_delete_category_route(client, auth_header):
    cat = seed_category(name="ToDelete")
    res = client.delete(f"/api/categories/{cat.id}", headers=auth_header)
    assert res.status_code == 200
    assert res.json["message"] == "Category deleted successfully"

    # Verify deletion
    assert Category.query.get(cat.id) is None
