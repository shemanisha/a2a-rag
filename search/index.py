from search.client import get_client

from config.settings import OPENSEARCH_INDEX


def create_index():

    client = get_client()


    if client.indices.exists(
        index=OPENSEARCH_INDEX
    ):

        print(
            f"Index '{OPENSEARCH_INDEX}' already exists"
        )

        return


    body = {

        "settings": {

            "index": {

                "knn": True

            }

        },


        "mappings": {

            "properties": {

                "document_id": {
                    "type": "keyword"
                },


                "chunk_id": {
                    "type": "keyword"
                },


                "filename": {
                    "type": "keyword"
                },


                "page_number": {
                    "type": "integer"
                },


                "content": {
                    "type": "text"
                },

                "file_hash": {
                    "type": "keyword"
                },

                "content_hash": {
                    "type": "keyword"
                },
                "document_version": {
                    "type": "integer"
                },


                "embedding": {

                    "type": "knn_vector",

                    "dimension": 384,

                    "method": {

                        "name": "hnsw",

                        "space_type": "cosinesimil",

                        "engine": "lucene"

                    }

                }

            }

        }

    }


    client.indices.create(
        index=OPENSEARCH_INDEX,
        body=body
    )


    print(
        f"Index '{OPENSEARCH_INDEX}' created"
    )

    # Create a separate index to store document-level metadata
    docs_index = f"{OPENSEARCH_INDEX}_documents"

    if client.indices.exists(index=docs_index):
        print(f"Index '{docs_index}' already exists")
        return

    docs_body = {
        "mappings": {
            "properties": {
                "document_id": {"type": "keyword"},
                "filename": {"type": "keyword"},
                "document_type": {"type": "keyword"},
                "department": {"type": "keyword"},
                "version": {"type": "integer"},
                "status": {"type": "keyword"},
                "file_hash": {"type": "keyword"},
                "content_hash": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        }
    }

    client.indices.create(index=docs_index, body=docs_body)

    print(f"Index '{docs_index}' created")