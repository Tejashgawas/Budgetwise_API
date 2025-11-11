# app/utils/auth_exceptions.py

class AuthBaseError(Exception):
    """Base class for all auth-related errors."""
    pass


class UserAlreadyExistsError(AuthBaseError):
    """Raised when a username or email already exists during registration."""
    pass


class InvalidCredentialsError(AuthBaseError):
    """Raised when login credentials are invalid."""
    pass


class UserNotFoundError(AuthBaseError):
    """Raised when the user is not found in the database."""
    pass


class TokenMissingError(AuthBaseError):
    """Raised when authentication token is missing or invalid."""
    pass


class TokenExpiredError(AuthBaseError):
    """Raised when JWT token is expired."""
    pass


class SecretKeyMissingError(AuthBaseError):
    """Raised when SECRET_KEY is missing from config."""
    pass

class TokenInvalidError(AuthBaseError):
    """Raised when JWT token is invalid."""
    pass


class TokenInvalidFormatError(AuthBaseError):
    """Raised when Authorization header format is invalid."""
    pass