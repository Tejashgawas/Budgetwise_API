import pytest
from unittest.mock import patch, MagicMock
from app.services.auth_services import AuthService
from app.utils.auth_exceptions import InvalidCredentialsError, UserAlreadyExistsError


# -----------------------------------
# REGISTER USER — UNIT TEST
# -----------------------------------
@patch("app.services.auth_services.User")
@patch("app.services.auth_services.db")
@patch("app.services.auth_services.hash_password", return_value="hashedpwd")
def test_register_user_success(mock_hash, mock_db, mock_user):
    mock_user.query.filter.return_value.first.return_value = None  # No user exists

    mock_new_user = MagicMock(id=1, username="tejas", email="t@example.com")
    mock_user.return_value = mock_new_user

    response, status = AuthService.register_user(
        username="tejas",
        email="t@example.com",
        password="mypassword"
    )

    assert status == 201
    assert response["message"] == "User registered successfully."
    assert response["user"]["username"] == "tejas"
    mock_db.session.add.assert_called_once()


# -----------------------------------
# REGISTER — USER ALREADY EXISTS
# -----------------------------------
@patch("app.services.auth_services.User")
def test_register_user_already_exists(mock_user):
    mock_user.query.filter.return_value.first.return_value = True

    with pytest.raises(UserAlreadyExistsError):
        AuthService.register_user("someone", "x@mail.com", "pass123")


# -----------------------------------
# LOGIN USER SUCCESS
# -----------------------------------
@patch("app.services.auth_services.User")
@patch("app.services.auth_services.verify_password", return_value=True)
@patch("app.services.auth_services.create_jwt_token", return_value="fake.jwt.token")
def test_login_success(mock_jwt, mock_verify, mock_user):
    mock_user.query.filter_by.return_value.first.return_value = MagicMock(
        id=1, username="tejas", email="test@mail.com", password_hash="hashed"
    )

    response, status = AuthService.login_user("test@mail.com", "123456")

    assert status == 200
    assert "token" in response
    assert response["token"] == "fake.jwt.token"


# -----------------------------------
# LOGIN — INVALID CREDENTIALS
# -----------------------------------
@patch("app.services.auth_services.User")
@patch("app.services.auth_services.verify_password", return_value=False)
def test_login_invalid_credentials(mock_verify, mock_user):
    mock_user.query.filter_by.return_value.first.return_value = MagicMock()

    with pytest.raises(InvalidCredentialsError):
        AuthService.login_user("wrong@mail.com", "badpass")