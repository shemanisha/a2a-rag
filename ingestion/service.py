import uuid

from ingestion.loader import (
    load_pdf
)

from ingestion.chunker import (
    create_chunks
)

from ingestion.embedder import (
    create_embeddings
)

from search.repository import (
    bulk_index_chunks
)


def ingest_document(
    file_path,
    filename
):

    # -----------------------
    # 1. Document ID
    # -----------------------

    document_id = str(
        uuid.uuid4()
    )


    # -----------------------
    # 2. Load PDF
    # -----------------------

    pages = load_pdf(
        file_path
    )


    print(
        f"Pages loaded: {len(pages)}"
    )


    # -----------------------
    # 3. Chunk
    # -----------------------

    chunks = create_chunks(
        pages
    )


    print(
        f"Chunks created: {len(chunks)}"
    )


    if len(chunks) == 0:

        raise ValueError(
            "No text found in document"
        )


    # -----------------------
    # 4. Get chunk texts
    # -----------------------

    texts = [

        chunk.text

        for chunk in chunks

    ]


    # -----------------------
    # 5. Embeddings
    # -----------------------

    embeddings = create_embeddings(
        texts
    )


    print(
        f"Embeddings created: {len(embeddings)}"
    )


    # -----------------------
    # 6. OpenSearch
    # -----------------------

    success, errors = bulk_index_chunks(

        document_id=document_id,

        filename=filename,

        chunks=chunks,

        embeddings=embeddings

    )


    return {

        "document_id":
            document_id,

        "filename":
            filename,

        "pages":
            len(pages),

        "chunks":
            len(chunks),

        "indexed_chunks":
            success,

        "failed_chunks":
            len(errors)

    }