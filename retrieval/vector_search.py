from ingestion.embedder import (
    create_embedding
)

from config.settings import (
    OPENSEARCH_INDEX,
    RETRIEVAL_TOP_K
)

from search.client import get_client


def vector_search(question:str):
    client = get_client()

    query_embedding = create_embedding(
        question
    )
    body = {
        "size": RETRIEVAL_TOP_K,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": RETRIEVAL_TOP_K
                }
            }
        }
    }
    client_response = client.search(
        index=OPENSEARCH_INDEX,
        body=body
    )
    return client_response["hits"]["hits"]