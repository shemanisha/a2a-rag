from typing import Optional

from search.client import get_client
from config.settings import OPENSEARCH_INDEX


def find_by_file_hash(file_hash: str) -> bool:
    client = get_client()

    q = {
        "query": {
            "term": {"file_hash": {"value": file_hash}}
        },
        "size": 1,
    }

    resp = client.search(index=OPENSEARCH_INDEX, body=q)
    return resp.get("hits", {}).get("total", {}).get("value", 0) > 0


def find_content_version(content_hash: str) -> Optional[int]:
    client = get_client()

    q = {
        "query": {
            "term": {"content_hash": {"value": content_hash}}
        },
        "size": 1,
        "_source": ["document_version"],
    }

    resp = client.search(index=OPENSEARCH_INDEX, body=q)
    hits = resp.get("hits", {}).get("hits", [])
    if not hits:
        return None

    src = hits[0].get("_source", {})
    return src.get("document_version")
