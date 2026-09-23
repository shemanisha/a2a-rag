from sentence_transformers import SentenceTransformer

from config.settings import EMBEDDING_MODEL


model = SentenceTransformer(
    EMBEDDING_MODEL
)


def create_embedding(text: str):

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def create_embeddings(
    texts: list[str]
):

    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True
    )

    return embeddings.tolist()