import uuid

from ingestion.validator import (
    validate_file_path,
    detect_mime_type,
)

from ingestion.extractors import (
    extract,
)

from ingestion.normalizer import (
    normalize_document,
)

from ingestion.chunker import (
    create_chunks,
)

from ingestion.embedder import (
    create_embeddings,
)

from search.repository import (
    bulk_index_chunks,
)
from search.documents import (
    upsert_document_metadata,
)
from search.search_helpers import (
    find_by_file_hash,
    find_content_version,
)
from ingestion.deduper import (
    sha256_file,
    sha256_text,
)


def ingest_document(file_path: str, filename: str, chunk_strategy: str | None = None):
    # 1. Validate file
    validate_file_path(file_path)

    # Extract
    kind = detect_mime_type(file_path)
    extracted = extract(file_path, kind)

    # Normalize
    pages = normalize_document(extracted)

    # Hash
    file_hash = sha256_file(file_path)

    content_concat = "\n".join(p.text for p in pages)
    content_hash = sha256_text(content_concat)

    # Duplicate check
    if find_by_file_hash(file_hash):
        return {
            "status": "SKIPPED",
            "reason": "file_already_exists"
        }

    existing_version = find_content_version(content_hash)

    # Document identity
    document_id = str(uuid.uuid4())
    document_version = (existing_version or 0) + 1

    # Create document metadata ONCE
    document_metadata = {
        "document_id": document_id,
        "filename": filename,
        "mime_type": kind,
        "document_type": extracted.metadata.get("document_type"),
        "department": extracted.metadata.get("department"),
        "version": document_version,
        "document_version": document_version,
        "file_hash": file_hash,
        "content_hash": content_hash,
    }

    # Create chunks WITH metadata
    chunks = create_chunks(
        pages,
        strategy=chunk_strategy,
        document_metadata=document_metadata,
    )

    # Embed
    texts = [chunk.text for chunk in chunks]
    embeddings = create_embeddings(texts)

    # Index
    success, errors = bulk_index_chunks(
        document_id=document_id,
        filename=filename,
        chunks=chunks,
        embeddings=embeddings,
    )

    # Store one document-level record
    upsert_document_metadata({
        **document_metadata,
        "status": "ACTIVE",
    })
    
    return {
        "document_id": document_id,
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "indexed_chunks": success,
        "failed_chunks": len(errors),
        "document_version": document_version,
        "file_hash": file_hash,
        "content_hash": content_hash,
    }


def ingest_file_simple(file_path: str, filename: str) -> dict:
    """Beginner-friendly ingestion: validate → extract → normalize → chunk → embed → index.

    This function intentionally keeps behavior simple so new contributors can follow the
    pipeline without advanced features like deduplication or versioning.
    """

    # 1. Validate
    validate_file_path(file_path)

    # 2. Extract
    kind = detect_mime_type(file_path)
    extracted = extract(file_path, kind)

    # 3. Normalize
    pages = normalize_document(extracted)

    # 4. Chunk
    chunks = create_chunks(pages)
    if not chunks:
        raise ValueError("No text after normalization")

    # 5. Embeddings
    texts = [c.text for c in chunks]
    embeddings = create_embeddings(texts)

    # 6. Index (use filename as a simple document_id for clarity)
    document_id = filename
    success, errors = bulk_index_chunks(
        document_id=document_id,
        filename=filename,
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "indexed": success,
        "errors": errors,
    }


def explain_simple() -> str:
    """Return a short explanation of each step for beginners."""

    return (
        "1. validate_file_path(file_path): checks the file exists and is a supported type.\n"
        "2. extract(file_path, kind): reads raw text from the file using the right parser.\n"
        "3. normalize_document(extracted): cleans whitespace and prepares pages for chunking.\n"
        "4. create_chunks(pages): splits pages into smaller chunks suitable for embeddings.\n"
        "5. create_embeddings(texts): converts each chunk into a numeric vector.\n"
        "6. bulk_index_chunks(...): stores chunk vectors and metadata in OpenSearch.\n"
    )