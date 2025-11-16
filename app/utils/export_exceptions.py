class ExportError(Exception):
    """Base exception for all export-related errors."""
    pass


class DateFormatError(ExportError):
    """Raised when start_date or end_date has invalid format."""
    #def __init__(self, message="Invalid date format. Expected YYYY-MM-DD."):
    #    super().__init__(message)
    pass


class EmptyTransactionError(ExportError):
    """Raised when no transactions exist for the user or time period."""
    #def __init__(self, message="No transactions found for the selected period."):
    #    super().__init__(message)
    pass


class PDFGenerationError(ExportError):
    """Raised when PDF generation fails (ReportLab errors, layout issues)."""
    #def __init__(self, message="PDF generation failed due to an internal error."):
    #    super().__init__(message)
    pass


class CSVGenerationError(ExportError):
    """Raised when CSV generation fails."""
    #def __init__(self, message="CSV generation failed due to an internal error."):
    #    super().__init__(message)
    pass


