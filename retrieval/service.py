from retrieval.hybrid_search import (
    hybrid_search
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
    question: str
):

    # 1. Hybrid retrieval

    candidates = hybrid_search(
        question
    )


    # 2. Rerank

    best_results = rerank(
        question,
        candidates
    )


    # 3. Context

    context = build_context(
        best_results
    )


    # 4. LLM

    answer = generate_answer(
        question,
        context
    )


    # 5. Sources

    sources = []


    for result in best_results:

        source = result[
            "_source"
        ]


        sources.append({

            "filename":
                source["filename"],

            "page_number":
                source["page_number"],

            "chunk_id":
                source["chunk_id"]

        })


    return {

        "question":
            question,

        "answer":
            answer,

        "sources":
            sources

    }