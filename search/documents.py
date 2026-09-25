from datetime import datetime
from search.client import get_client
from config.settings import OPENSEARCH_INDEX


def docs_index_name() -> str:
    return f"{OPENSEARCH_INDEX}_documents"


def upsert_document_metadata(metadata: dict):
    client = get_client()
    idx = docs_index_name()

    doc_id = metadata.get("document_id")
    if not doc_id:
        raise ValueError("document_id required")

    body = metadata.copy()
    body.setdefault("created_at", datetime.utcnow().isoformat())

    client.index(index=idx, id=doc_id, body=body)


def get_document(document_id: str):
    client = get_client()
    idx = docs_index_name()

    try:
        resp = client.get(index=idx, id=document_id)
        return resp.get("_source")
    except Exception:
        return None
