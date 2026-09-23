from dataclasses import dataclass

from langchain_community.document_loaders import (
    PyPDFLoader
)


@dataclass
class LoadedPage:

    text: str

    page_number: int


def load_pdf(
    file_path: str
):

    loader = PyPDFLoader(
        file_path
    )


    pages = loader.load()


    loaded_pages = []


    for page in pages:

        loaded_page = LoadedPage(

            text=page.page_content,

            page_number=page.metadata.get(
                "page",
                0
            )

        )


        loaded_pages.append(
            loaded_page
        )


    return loaded_pages