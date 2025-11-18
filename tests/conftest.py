import pytest
from app import create_app
from app.extensions import db as _db
from app.utils.security import create_jwt_token


# -----------------------------
# 1. Create a fresh Test App
# -----------------------------
@pytest.fixture()
def app():
    import os
    os.environ["FLASK_ENV"] = "testing"

    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "test-secret-key"

    # Push context
    ctx = app.app_context()
    ctx.push()

    # Create new tables before each test
    _db.create_all()

    yield app

    # Cleanup
    _db.session.remove()
    _db.drop_all()
    ctx.pop()


# -----------------------------
# 2. DB Fixture (simple)
# -----------------------------
@pytest.fixture()
def db(app):
    return _db


# -----------------------------
# 3. Test Client
# -----------------------------
@pytest.fixture()
def client(app):
    return app.test_client()


# -----------------------------
# 4. Auth Header Fixture
# -----------------------------
@pytest.fixture()
def auth_header():
    """Generates a clean Authorization header with no weird unicode spaces."""
    token = create_jwt_token(user_id=1)
    return {"Authorization": f"Bearer {token}"}
