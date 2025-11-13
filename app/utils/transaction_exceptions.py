# app/utils/transaction_exceptions.py

class TransactionError(Exception):
    """Base class for all transaction-related errors."""
    pass


# -------------------------------
# Validation / Input Errors
# -------------------------------
class InvalidTransactionDataError(TransactionError):
    """Raised when transaction data is invalid or incomplete."""
    pass


class CategoryNotFoundError(TransactionError):
    """Raised when the referenced category does not exist."""
    pass


class DuplicateTransactionError(TransactionError):
    """Raised when attempting to create a duplicate transaction."""
    pass


# -------------------------------
# CRUD Operation Errors
# -------------------------------
class TransactionNotFoundError(TransactionError):
    """Raised when a transaction is not found."""
    pass


class TransactionUpdateError(TransactionError):
    """Raised when updating a transaction fails."""
    pass


class TransactionDeleteError(TransactionError):
    """Raised when deleting a transaction fails."""
    pass


# -------------------------------
# Database / Server Errors
# -------------------------------
class TransactionDatabaseError(TransactionError):
    """Raised for unexpected DB commit or query errors."""
    pass
