class ExportError(Exception):
    """Base exception for all export-related errors."""
    pass


class DateFormatError(ExportError):
    """Raised when start_date or end_date has invalid format."""
    pass


class EmptyTransactionError(ExportError):
    """Raised when no transactions exist for the user or time period."""
    pass


class PDFGenerationError(ExportError):
    """Raised when PDF generation fails (ReportLab errors, layout issues)."""
    pass


class CSVGenerationError(ExportError):
    """Raised when CSV generation fails."""
    pass

