import os
import shutil
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from pydantic import BaseModel

from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import get_db
from models.document import Document

from rag.service import (
    index_document,
    search_documents
)

from services.ollama_service import (
    generate_answer
)


router = APIRouter()


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    question: str
    document_id: int


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ============================================================
# STATUS
# ============================================================

@router.get("/status")
def get_status():

    return {
        "project": "AISoC",
        "status": "running",
        "message": "AISoC backend is working"
    }


# ============================================================
# DATABASE STATUS
# ============================================================

@router.get("/database-status")
def database_status(
    db: Session = Depends(get_db)
):

    result = db.execute(
        text("SELECT current_database()")
    )

    database_name = result.scalar()

    return {
        "database": database_name,
        "status": "connected"
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    document = Document(
        filename=file.filename,
        file_type=file.content_type,
        file_path=file_path,
        upload_date=datetime.utcnow(),
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    indexed_chunks = 0

    # --------------------------------------------------------
    # INDEX PDF
    # --------------------------------------------------------

    if file.filename.lower().endswith(".pdf"):

        try:

            indexed_chunks = index_document(
                document.id,
                document.filename,
                document.file_path
            )

            document.status = "processed"

            db.commit()

        except Exception as e:

            document.status = "uploaded"

            db.commit()

            print(
                f"RAG indexing failed: {e}"
            )

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "status": document.status,
        "indexed_chunks": indexed_chunks
    }


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get("/documents")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = db.query(
        Document
    ).order_by(
        Document.upload_date.desc()
    ).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_path": document.file_path,
            "upload_date": document.upload_date,
            "status": document.status
        }
        for document in documents
    ]


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

@router.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_path": document.file_path,
        "upload_date": document.upload_date,
        "status": document.status
    }


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # --------------------------------------------------------
    # DELETE PHYSICAL FILE
    # --------------------------------------------------------

    if (
        document.file_path
        and os.path.exists(document.file_path)
    ):

        os.remove(
            document.file_path
        )

    # --------------------------------------------------------
    # DELETE DATABASE RECORD
    # --------------------------------------------------------

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }


# ============================================================
# CHAT
# ============================================================

@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    question = request.question.strip()

    document_id = request.document_id

    # --------------------------------------------------------
    # VALIDATE QUESTION
    # --------------------------------------------------------

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # --------------------------------------------------------
    # VERIFY DOCUMENT
    # --------------------------------------------------------

    document = db.query(
        Document
    ).filter(
        Document.id == document_id
    ).first()

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Selected document not found"
        )

    # --------------------------------------------------------
    # SEARCH ONLY SELECTED DOCUMENT
    # --------------------------------------------------------

    search_results = search_documents(
        question,
        document_id=document_id,
        n_results=5
    )

    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not search_results:

        return {
            "question": question,
            "document_id": document_id,
            "document": document.filename,
            "answer": (
                "I couldn't find any relevant information "
                "about this question in the selected document."
            ),
            "sources": []
        }

    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    sources = []

    for result in search_results:

        context_parts.append(
            result["document"]
        )

        sources.append(
            {
                "filename": result["filename"],
                "document_id": int(
                    result["document_id"]
                ),
                "content": result["document"]
            }
        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # GENERATE AI ANSWER
    # --------------------------------------------------------

    try:

        answer = generate_answer(
            question,
            context
        )

    except Exception as e:

        print(
            f"Ollama error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "AI generation failed. "
                "Make sure Ollama is running "
                "and the configured model is available."
            )
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "question": question,
        "document_id": document_id,
        "document": document.filename,
        "answer": answer,
        "sources": sources
    }