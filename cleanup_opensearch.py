from search.client import get_client
from search.index import create_index
from config.settings import OPENSEARCH_INDEX


client = get_client()


def reset_index():
    try:
        if client.indices.exists(index=OPENSEARCH_INDEX):
            client.indices.delete(index=OPENSEARCH_INDEX)
            print(f"Deleted index: {OPENSEARCH_INDEX}")

        create_index()
        print(f"Recreated index: {OPENSEARCH_INDEX}")

    except Exception as e:
        print(f"Error resetting index: {e}")


def delete_documents_by_filename(filename: str):
    try:
        response = client.delete_by_query(
            index=OPENSEARCH_INDEX,
            body={
                "query": {
                    "term": {
                        "filename.keyword": filename
                    }
                }
            }
        )
        print(f"Deleted documents for {filename}: {response}")

    except Exception as e:
        print(f"Error deleting documents for {filename}: {e}")


def delete_all_documents():
    try:
        response = client.delete_by_query(
            index=OPENSEARCH_INDEX,
            body={
                "query": {
                    "match_all": {}
                }
            }
        )
        print(f"Deleted all documents: {response}")

    except Exception as e:
        print(f"Error deleting all documents: {e}")


if __name__ == "__main__":
    # Choose one:
    reset_index()
    # delete_documents_by_filename("01_employee_leave_policy.pdf")
    # delete_all_documents()
