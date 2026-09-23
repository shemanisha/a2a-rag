from search.client import (
    get_client
)

from config.settings import (
    OPENSEARCH_INDEX,
    RETRIEVAL_TOP_K
)


def bm25_search(
    question: str
):

    client = get_client()


    body = {

        "size":
            RETRIEVAL_TOP_K,

        "query": {

            "match": {

                "content":
                    question

            }

        }

    }


    response = client.search(

        index=OPENSEARCH_INDEX,

        body=body

    )


    return response[
        "hits"
    ]["hits"]