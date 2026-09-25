from ingestion.embedder import create_embedding

from config.settings import (
    OPENSEARCH_INDEX,
    RETRIEVAL_TOP_K,
)

from search.client import get_client

from retrieval.filters import (
    build_filters
)


def vector_search(
    question: str,
    top_k: int | None = None,
    metadata_filters: dict | None = None,
    min_score: float | None = None,
):

    client = get_client()

    k = (
        top_k
        if top_k is not None
        else RETRIEVAL_TOP_K
    )

    if k <= 0:
        raise ValueError(
            "top_k must be greater than 0"
        )

    # --------------------------------
    # 1. Question → embedding
    # --------------------------------

    query_embedding = create_embedding(
        question
    )

    # --------------------------------
    # 2. Metadata filters
    # --------------------------------

    filters = build_filters(
        metadata_filters
    )

    # --------------------------------
    # 3. Vector query
    # --------------------------------

    body = {
        "size": k,
        "query": {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "embedding": {
                                "vector":
                                    query_embedding,

                                "k":
                                    k
                            }
                        }
                    }
                ],
                "filter": filters
            }
        }
    }

    # --------------------------------
    # 4. Search
    # --------------------------------

    response = client.search(
        index=OPENSEARCH_INDEX,
        body=body
    )

    hits = (
        response
        .get("hits", {})
        .get("hits", [])
    )

    # --------------------------------
    # 5. Optional score filtering
    # --------------------------------

    if min_score is not None:

        hits = [
            hit
            for hit in hits
            if hit.get("_score", 0)
            >= min_score
        ]

    return hits