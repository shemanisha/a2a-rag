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

    # 2. Detect type and extract
    kind = detect_mime_type(file_path)

    extracted = extract(file_path, kind)

    # 3. Normalize / clean extracted text and create pages
    pages = normalize_document(extracted)

    # 3b. File hash and content hash for deduplication
    file_hash = sha256_file(file_path)

    # content-level hash: concatenate cleaned pages
    content_concat = "\n".join([p.text for p in pages])
    content_hash = sha256_text(content_concat)

    # Pre-index duplicate checks
    if find_by_file_hash(file_hash):
        return {
            "status": "SKIPPED",
            "reason": "file_already_exists",
            "file_hash": file_hash,
        }

    existing_version = find_content_version(content_hash)

    # 3. Document ID and metadata
    document_id = str(uuid.uuid4())
    document_version = (existing_version or 0) + 1

    print(f"Pages loaded: {len(pages)} | format: {extracted.metadata.get('format')}")

    # 4. Chunk
    chunks = create_chunks(pages, strategy=chunk_strategy)

    print(f"Chunks created: {len(chunks)}")

    if len(chunks) == 0:
        raise ValueError("No text found in document")

    # 5. Get chunk texts
    texts = [chunk.text for chunk in chunks]

    # 6. Embeddings
    embeddings = create_embeddings(texts)

    print(f"Embeddings created: {len(embeddings)}")

    # Attach hashes to chunks for indexing
    for c in chunks:
        setattr(c, "file_hash", file_hash)
        setattr(c, "content_hash", content_hash)
        setattr(c, "document_version", document_version)

    # 7. OpenSearch
    success, errors = bulk_index_chunks(
        document_id=document_id,
        filename=filename,
        chunks=chunks,
        embeddings=embeddings,
    )

    # Persist document-level metadata
    upsert_document_metadata(
        {
            "document_id": document_id,
            "filename": filename,
            "document_type": extracted.metadata.get("document_type"),
            "department": extracted.metadata.get("department"),
            "version": document_version,
            "status": "ACTIVE",
            "file_hash": file_hash,
            "content_hash": content_hash,
        }
    )

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