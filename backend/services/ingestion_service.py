from services.document_processor import extract_text
from services.chunker import chunk_text
from services.embedding_service import generate_embeddings
from services.vector_store import add_documents


def ingest_document(
    file_path: str,
    document_id: int,
    filename: str
):
    text = extract_text(file_path)

    chunks = chunk_text(text)

    if not chunks:
        return {
            "status": "failed",
            "message": "No text could be extracted"
        }

    embeddings = generate_embeddings(chunks)

    ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    add_documents(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    return {
        "status": "processed",
        "document_id": document_id,
        "chunks": len(chunks)
    }