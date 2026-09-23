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