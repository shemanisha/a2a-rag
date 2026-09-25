import os
from pathlib import Path


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".html",
    ".htm",
    ".csv",
}


def validate_file_path(file_path: str) -> bool:
    """Ensure the file exists and has an allowed extension."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    ext = path.suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    return True


def detect_mime_type(file_path: str) -> str:
    """Return a simple mime/type label used by extractors."""
    ext = Path(file_path).suffix.lower()

    if ext in {".pdf"}:
        return "pdf"

    if ext in {".docx"}:
        return "docx"

    if ext in {".html", ".htm"}:
        return "html"

    if ext in {".csv"}:
        return "csv"

    return "unknown"
