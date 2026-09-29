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


class ChatRequest(BaseModel):
    question: str


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


@router.get("/status")
def get_status():
    return {
        "project": "AISoC",
        "status": "running",
        "message": "AISoC backend is working"
    }


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

    with open(file_path, "wb") as buffer:
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

    if document.file_path and os.path.exists(
        document.file_path
    ):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }


@router.post("/chat")
def chat(
    request: ChatRequest
):
    question = request.question

    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    chunks = search_documents(
        question,
        n_results=5
    )

    if not chunks:
        return {
            "question": question,
            "answer": (
                "No relevant information was "
                "found in the uploaded documents."
            ),
            "sources": []
        }

    context = "\n\n".join(chunks)

    answer = generate_answer(
        question,
        context
    )

    return {
        "question": question,
        "answer": answer,
        "sources": chunks
    }