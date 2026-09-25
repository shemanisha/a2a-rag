def build_context(
    results
):

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        source = result[
            "_source"
        ]

        text = f"""
[SOURCE {index}]

File: {source['filename']}
Page: {source['page_number']}
Chunk ID: {source['chunk_id']}

{source['content']}
""".strip()

        context_parts.append(
            text
        )

    return "\n\n---\n\n".join(
        context_parts
    )