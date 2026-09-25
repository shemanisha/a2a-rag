from retrieval.vector_search import (
    vector_search
)

from retrieval.bm25_search import (
    bm25_search
)


RRF_K = 60


def hybrid_search(
    question: str,
    top_k: int | None = None,
    metadata_filters: dict | None = None,
    vector_min_score: float | None = None,
):

    # --------------------------------
    # 1. Vector search
    # --------------------------------

    vector_results = vector_search(
        question=question,
        top_k=top_k,
        metadata_filters=metadata_filters,
        min_score=vector_min_score,
    )

    # --------------------------------
    # 2. BM25 search
    # --------------------------------

    bm25_results = bm25_search(
        question=question,
        top_k=top_k,
        metadata_filters=metadata_filters,
    )

    scores = {}

    chunks = {}

    # --------------------------------
    # 3. Vector RRF scores
    # --------------------------------

    for rank, result in enumerate(
        vector_results,
        start=1
    ):

        chunk_id = result["_id"]

        chunks[chunk_id] = result

        scores[chunk_id] = (
            scores.get(
                chunk_id,
                0
            )
            +
            1 / (
                RRF_K + rank
            )
        )

    # --------------------------------
    # 4. BM25 RRF scores
    # --------------------------------

    for rank, result in enumerate(
        bm25_results,
        start=1
    ):

        chunk_id = result["_id"]

        chunks[chunk_id] = result

        scores[chunk_id] = (
            scores.get(
                chunk_id,
                0
            )
            +
            1 / (
                RRF_K + rank
            )
        )

    # --------------------------------
    # 5. Sort by RRF
    # --------------------------------

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    results = []

    for chunk_id in ranked_ids:

        result = chunks[chunk_id]

        # Save RRF score
        # Useful later for debugging
        # and evaluation.

        result["rrf_score"] = (
            scores[chunk_id]
        )

        results.append(
            result
        )

    return results