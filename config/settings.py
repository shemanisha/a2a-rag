import os

from dotenv import load_dotenv


load_dotenv()


OPENSEARCH_HOST = os.getenv(
    "OPENSEARCH_HOST",
    "localhost"
)

OPENSEARCH_PORT = int(
    os.getenv(
        "OPENSEARCH_PORT",
        "9200"
    )
)

OPENSEARCH_INDEX = os.getenv(
    "OPENSEARCH_INDEX",
    "rag_documents"
)


EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:1b"
)


CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "800"
    )
)


CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "100"
    )
)


RETRIEVAL_TOP_K = int(
    os.getenv(
        "RETRIEVAL_TOP_K",
        "20"
    )
)


RERANK_TOP_K = int(
    os.getenv(
        "RERANK_TOP_K",
        "5"
    )
)