"""Optional historical financial appendix for Gmail detailed report.

No network, file writes, or message sending. Only reads an explicit preview path.
"""
from pathlib import Path
from financial_review_report import render_from_file


def append_historical_financial_review(detailed: str, preview_path: str | Path | None = None) -> str:
    """Return the original report unchanged when preview is absent or invalid."""
    if not isinstance(detailed, str):
        raise TypeError('DetailedReportMustBeString')
    if preview_path is None:
        return detailed
    try:
        appendix = render_from_file(preview_path)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        return detailed
    return detailed + '\n\n' + appendix if appendix else detailed
