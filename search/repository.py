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

        if getattr(chunk, "file_hash", None):
            action["_source"]["file_hash"] = chunk.file_hash

        if getattr(chunk, "content_hash", None):
            action["_source"]["content_hash"] = chunk.content_hash
        if getattr(chunk, "document_version", None):
            action["_source"]["document_version"] = chunk.document_version


        actions.append(
            action
        )


    success, errors = bulk(client, actions, raise_on_error=False)


    client.indices.refresh(
        index=OPENSEARCH_INDEX
    )


    return success, errors