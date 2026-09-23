from dataclasses import dataclass

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


@dataclass
class Chunk:

    text: str

    page_number: int


splitter = RecursiveCharacterTextSplitter(

    chunk_size=CHUNK_SIZE,

    chunk_overlap=CHUNK_OVERLAP

)


def create_chunks(
    pages
):

    chunks = []


    for page in pages:

        texts = splitter.split_text(
            page.text
        )


        for text in texts:

            chunk = Chunk(

                text=text,

                page_number=page.page_number

            )


            chunks.append(
                chunk
            )


    return chunks