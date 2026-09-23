import os

from dotenv import load_dotenv


load_dotenv()


OPENSEARCH_HOST = os.getenv(
    "OPENSEARCH_HOST"
)

OPENSEARCH_PORT = int(
    os.getenv(
        "OPENSEARCH_PORT"
    )
)

OPENSEARCH_INDEX = os.getenv(
    "OPENSEARCH_INDEX"
)


EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL"
)


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL"
)


CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE"
    )
)


CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP"
    )
)


RETRIEVAL_TOP_K = int(
    os.getenv(
        "RETRIEVAL_TOP_K"
    )
)


RERANK_TOP_K = int(
    os.getenv(
        "RERANK_TOP_K"
    )
)