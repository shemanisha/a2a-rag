from sentence_transformers import (
    CrossEncoder
)

from config.settings import (
    RERANK_TOP_K
)


model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank(
    question: str,
    results
):

    if not results:
        return []

    pairs = []

    for result in results:

        content = result[
            "_source"
        ]["content"]

        pairs.append(
            [
                question,
                content
            ]
        )

    scores = model.predict(
        pairs
    )

    ranked = []

    for result, score in zip(
        results,
        scores
    ):

        result[
            "reranker_score"
        ] = float(score)

        ranked.append(
            result
        )

    ranked.sort(
        key=lambda result:
            result[
                "reranker_score"
            ],
        reverse=True
    )

    # Apply thresholding: only keep items with positive (or sufficiently high) reranker score.
    # If you want a configurable cutoff, move this to settings.
    filtered = [r for r in ranked if r["reranker_score"] is not None and r["reranker_score"] > -10.0]

    return filtered[:RERANK_TOP_K]