from app.models.user import User
from app.extensions import db


# -----------------------------------
# REGISTER SUCCESS
# -----------------------------------
def test_register_integration(client):
    res = client.post("/api/auth/register", json={
        "username": "tejas",
        "email": "t@example.com",
        "password": "password123"
    })

    assert res.status_code == 201
    data = res.json

    assert data["message"] == "User registered successfully."
    assert data["user"]["username"] == "tejas"
    assert data["user"]["email"] == "t@example.com"


# -----------------------------------
# REGISTER FAIL (duplicate)
# -----------------------------------
def test_register_duplicate(client):
    # First registration
    client.post("/api/auth/register", json={
        "username": "tejas",
        "email": "t@example.com",
        "password": "password123"
    })

    # Duplicate email
    res = client.post("/api/auth/register", json={
        "username": "tejas",
        "email": "t@example.com",
        "password": "password123"
    })

    assert res.status_code == 400
    assert "exists" in res.json["message"].lower()


# -----------------------------------
# LOGIN SUCCESS
# -----------------------------------
def test_login_integration(client):
    # Create a user first
    client.post("/api/auth/register", json={
        "username": "tejas",
        "email": "t@example.com",
        "password": "password123"
    })

    res = client.post("/api/auth/login", json={
        "email": "t@example.com",
        "password": "password123"
    })

    assert res.status_code == 200
    assert "token" in res.json
    assert res.json["user"]["email"] == "t@example.com"


# -----------------------------------
# LOGIN FAIL
# -----------------------------------
def test_login_invalid(client):
    res = client.post("/api/auth/login", json={
        "email": "wrong@mail.com",
        "password": "nope"
    })

    assert res.status_code == 401
    assert "invalid" in res.json["message"].lower()


# -----------------------------------
# GET CURRENT USER (/me)
# -----------------------------------
def test_get_current_user(client, auth_header):
    # Insert a user manually into DB
    user = User(username="tejas", email="t@example.com", password_hash="x")
    db.session.add(user)
    db.session.commit()

    # Auth header always uses user_id=1 in our fixture
    res = client.get("/api/auth/me", headers=auth_header)

    assert res.status_code == 200
    assert res.json["email"] == "t@example.com"
    assert "created_at" in res.json


# -----------------------------------
# LOGOUT
# -----------------------------------
def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert res.json["message"].lower() == "logout successful."