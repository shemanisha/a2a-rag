from opensearchpy.helpers import bulk

from search.client import get_client

from config.settings import (
    OPENSEARCH_INDEX
)
from search.search_helpers import (
    find_content_version,
)


def bulk_index_chunks(
    document_id,
    filename,
    chunks,
    embeddings
):

    client = get_client()


    actions = []


    for index, chunk in enumerate(chunks):

        chunk_id = (
            f"{document_id}-{index}"
        )



        # Optional fields file_hash/content_hash may be set on chunk
        action = {
            "_index": OPENSEARCH_INDEX,
            "_id": chunk_id,
            "_source": {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "filename": filename,
                "page_number": chunk.page_number,
                "content": chunk.text,
                "embedding": embeddings[index],
            },
        }

        # Preserve common document metadata fields if present on chunk
        for meta_field in ("file_hash", "content_hash", "document_version", "mime_type", "department", "document_type"):
            if getattr(chunk, meta_field, None) is not None:
                action["_source"][meta_field] = getattr(chunk, meta_field)

        # Also copy any additional simple attrs from chunk that are strings/ints
        # to support flexible metadata without changing the mapping.
        for attr in dir(chunk):
            if attr.startswith("_"):
                continue
            if attr in ("text", "page_number", "parent_id"):
                continue
            if attr in ("file_hash", "content_hash", "document_version", "mime_type", "department", "document_type"):
                continue
            try:
                val = getattr(chunk, attr)
            except Exception:
                continue
            if isinstance(val, (str, int, float, bool)):
                action["_source"][attr] = val


        actions.append(
            action
        )


    success, errors = bulk(client, actions, raise_on_error=False)


    client.indices.refresh(
        index=OPENSEARCH_INDEX
    )


    return success, errors