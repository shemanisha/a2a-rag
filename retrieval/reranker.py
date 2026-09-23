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
    question,
    results
):

    if not results:

        return []


    pairs = []


    for result in results:

        text = result[
            "_source"
        ]["content"]


        pairs.append(
            [
                question,
                text
            ]
        )


    scores = model.predict(
        pairs
    )


    ranked = list(
        zip(
            results,
            scores
        )
    )


    ranked.sort(

        key=lambda item:
            item[1],

        reverse=True

    )


    return [

        result

        for result, score
        in ranked[
            :RERANK_TOP_K
        ]

    ]