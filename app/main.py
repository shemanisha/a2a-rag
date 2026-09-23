import os
import shutil
import tempfile

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from ingestion.service import (
    ingest_document
)

from search.index import (
    create_index
)

from pydantic import BaseModel

from retrieval.service import (
    ask_question
)

class QuestionRequest(
    BaseModel
):

    question: str


app = FastAPI(

    title="Production RAG API",

    version="1.0.0"

)


@app.on_event("startup")
def startup():

    create_index()


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post(
    "/api/v1/documents"
)
async def upload_document(

    file: UploadFile = File(...)

):

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension != ".pdf":

        raise HTTPException(

            status_code=400,

            detail="For now only PDF is supported"

        )


    temp_path = None


    try:

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=".pdf"

        ) as temp_file:


            shutil.copyfileobj(

                file.file,

                temp_file

            )


            temp_path = (
                temp_file.name
            )


        result = ingest_document(

            file_path=temp_path,

            filename=file.filename

        )


        return {

            "status": "SUCCESS",

            "data": result

        }


    finally:

        if (
            temp_path
            and
            os.path.exists(temp_path)
        ):

            os.remove(
                temp_path
            )
    




@app.post(
    "/api/v1/ask"
)
def ask(
    request: QuestionRequest
):

    return ask_question(
        request.question
    )