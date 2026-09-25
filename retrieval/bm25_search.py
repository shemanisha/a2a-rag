from search.client import get_client

from config.settings import (
    OPENSEARCH_INDEX,
    RETRIEVAL_TOP_K
)

from retrieval.filters import (
    build_filters
)


def bm25_search(
    question: str,
    top_k: int | None = None,
    metadata_filters: dict | None = None,
):

    client = get_client()

    k = (
        top_k
        if top_k is not None
        else RETRIEVAL_TOP_K
    )

    filters = build_filters(
        metadata_filters
    )

    body = {
        "size": k,
        "query": {
            "bool": {

                "must": [
                    {
                        "match": {
                            "content":
                                question
                        }
                    }
                ],

                "filter":
                    filters
            }
        }
    }

    response = client.search(
        index=OPENSEARCH_INDEX,
        body=body
    )

    return (
        response
        .get("hits", {})
        .get("hits", [])
    )