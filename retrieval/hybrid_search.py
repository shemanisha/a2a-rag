from retrieval.vector_search import (
    vector_search
)

from retrieval.bm25_search import (
    bm25_search
)



def hybrid_search(
    question
):

    vector_results = vector_search(
        question
    )

    bm25_results = bm25_search(
        question
    )


    scores = {}

    documents = {}


    RRF_K = 60


    # Vector results

    for rank, result in enumerate(
        vector_results,
        start=1
    ):

        document_id = result["_id"]

        documents[
            document_id
        ] = result


        scores[
            document_id
        ] = (

            scores.get(
                document_id,
                0
            )

            +

            1 / (
                RRF_K + rank
            )

        )


    # BM25 results

    for rank, result in enumerate(
        bm25_results,
        start=1
    ):

        document_id = result["_id"]

        documents[
            document_id
        ] = result


        scores[
            document_id
        ] = (

            scores.get(
                document_id,
                0
            )

            +

            1 / (
                RRF_K + rank
            )

        )


    ranked_ids = sorted(

        scores,

        key=scores.get,

        reverse=True

    )


    results = [

        documents[
            document_id
        ]

        for document_id
        in ranked_ids

    ]


    return results