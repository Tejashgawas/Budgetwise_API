class SummaryError(Exception):
    """Base class for all summary-related errors."""

    pass

class MissingParameterError(SummaryError):
    """Raised when required query parameters (start, end, etc.) are missing."""
    pass

class InvalidPeriodTypeError(SummaryError):
    """Raised when an unsupported period_type is provided."""
    pass

class SummaryNotFoundError(SummaryError):
    """Raised when no transactions exist for the selected period."""
    pass

class SummaryDatabaseError(SummaryError):
    """Raised for unexpected database or computation errors."""
    pass