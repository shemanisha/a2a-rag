from retrieval.hybrid_search import (
    hybrid_search
)

from retrieval.deduplicator import (
    remove_duplicate_results
)

from retrieval.reranker import (
    rerank
)

from retrieval.context_builder import (
    build_context
)

from retrieval.generator import (
    generate_answer
)


def ask_question(
    question: str,
    metadata_filters: dict | None = None,
):

    # --------------------------------
    # 1. Hybrid retrieval
    # --------------------------------

    candidates = hybrid_search(
        question=question,
        metadata_filters=metadata_filters,
    )

    # --------------------------------
    # 2. Remove duplicates
    # --------------------------------

    unique_candidates = (
        remove_duplicate_results(
            candidates
        )
    )

    # --------------------------------
    # 3. Rerank
    # --------------------------------

    best_results = rerank(
        question,
        unique_candidates
    )

    # --------------------------------
    # 4. No evidence
    # --------------------------------

    if not best_results:

        return {
            "question":
                question,

            "answer":
                "I don't have enough information in the provided documents.",

            "sources":
                []
        }

    # --------------------------------
    # 5. Build context
    # --------------------------------

    context = build_context(
        best_results
    )

    # --------------------------------
    # 6. Generate answer
    # --------------------------------

    answer = generate_answer(
        question,
        context
    )

    # --------------------------------
    # 7. Trusted source metadata
    # --------------------------------

    sources = []

    for index, result in enumerate(
        best_results,
        start=1
    ):

        source = result[
            "_source"
        ]

        sources.append({
            "source_id":
                index,

            "document_id":
                source.get(
                    "document_id"
                ),

            "chunk_id":
                source.get(
                    "chunk_id"
                ),

            "filename":
                source.get(
                    "filename"
                ),

            "page_number":
                source.get(
                    "page_number"
                ),

            "rrf_score":
                result.get(
                    "rrf_score"
                ),

            "reranker_score":
                result.get(
                    "reranker_score"
                )
        })

    return {
        "question":
            question,

        "answer":
            answer,

        "sources":
            sources
    }