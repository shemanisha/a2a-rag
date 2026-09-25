import re


def normalize_text(
    text: str
):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def remove_duplicate_results(
    results
):

    seen_chunk_ids = set()

    seen_content = set()

    unique_results = []

    for result in results:

        source = result[
            "_source"
        ]

        chunk_id = source[
            "chunk_id"
        ]

        content = normalize_text(
            source["content"]
        )

        # Same chunk
        if chunk_id in seen_chunk_ids:
            continue

        # Same textual content
        if content in seen_content:
            continue

        seen_chunk_ids.add(
            chunk_id
        )

        seen_content.add(
            content
        )

        unique_results.append(
            result
        )

    return unique_results