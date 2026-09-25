import re
from typing import List

from ingestion.extractors import ExtractedDocument
from ingestion.loader import LoadedPage


RE_WHITESPACE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if text is None:
        return ""

    # Remove null bytes and non-printable control chars
    text = text.replace("\x00", " ")

    # Normalize whitespace
    text = RE_WHITESPACE.sub(" ", text)

    # Trim
    text = text.strip()

    return text


def normalize_document(extracted: ExtractedDocument) -> List[LoadedPage]:
    """Return a list of LoadedPage objects with cleaned text.

    For CSV/Excel we treat each row as a separate page so downstream
    chunking can be row-aware.
    """
    fmt = extracted.metadata.get("format", "")

    normalized: List[LoadedPage] = []

    if fmt in ("csv", "excel"):
        # expect a single page containing all rows
        if not extracted.pages:
            return []

        all_text = extracted.pages[0].text
        rows = [r for r in all_text.splitlines()]

        for idx, row in enumerate(rows):
            text = clean_text(row)
            if text:
                normalized.append(LoadedPage(text=text, page_number=idx))

        return normalized

    # Default: clean each page
    for p in extracted.pages:
        text = clean_text(p.text)
        if text:
            normalized.append(LoadedPage(text=text, page_number=p.page_number))

    return normalized
