# app/utils/category_exceptions.py

class CategoryError(Exception):
    """Base class for all category-related errors."""
    pass


# -------------------------------
# Validation / Input Errors
# -------------------------------
class CategoryAlreadyExistsError(CategoryError):
    """Raised when user tries to create a duplicate category."""
    pass


class InvalidCategoryTypeError(CategoryError):
    """Raised when category type is invalid."""
    pass


# -------------------------------
# CRUD Operation Errors
# -------------------------------
class CategoryNotFoundError(CategoryError):
    """Raised when category is not found or user has no access."""
    pass


class CategoryDatabaseError(CategoryError):
    """Raised when a DB operation fails."""
    pass
