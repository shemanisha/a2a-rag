import ollama

from config.settings import (
    OLLAMA_MODEL
)


def generate_answer(
    question,
    context
):

    prompt = f"""
Use only the provided context.
Answer the question with a single exact value or sentence.
Do not add extra explanation.
Do not paraphrase.
Do not include source names or page numbers.
If the answer is not in the context, reply exactly:
I don't have enough information in the provided document.

Context:
{context}

Question:
{question}

Answer:
"""


    response = ollama.chat(

        model=OLLAMA_MODEL,

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]

    )


    return response[
        "message"
    ]["content"]