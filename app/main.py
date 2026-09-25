import os
import shutil
import tempfile

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Form,
)

from ingestion.service import (
    ingest_document
)

from ingestion.validator import (
    ALLOWED_EXTENSIONS,
)
from ingestion.chunker import (
    SUPPORTED_STRATEGIES,
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
    file: UploadFile = File(...),
    chunk_strategy: str | None = Form(default=None),
):

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(f"Unsupported file type: {extension}. "
                    f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"),
        )


    temp_path = None


    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:


            shutil.copyfileobj(

                file.file,

                temp_file

            )


            temp_path = (
                temp_file.name
            )


        # Validate provided chunk strategy
        if chunk_strategy is not None and chunk_strategy not in SUPPORTED_STRATEGIES:
            raise HTTPException(status_code=400, detail=f"Unsupported chunk strategy: {chunk_strategy}")

        result = ingest_document(
            file_path=temp_path,
            filename=file.filename,
            chunk_strategy=chunk_strategy,
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