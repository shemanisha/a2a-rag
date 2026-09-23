def build_context(
    results
):

    context_parts = []


    for result in results:

        source = result[
            "_source"
        ]


        text = f"""
Source: {source['filename']}
Page: {source['page_number']}

{source['content']}
"""


        context_parts.append(
            text
        )


    return "\n\n---\n\n".join(
        context_parts
    )