import os

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_or_create_collection(
    name="aisoc_documents"
)


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def index_document(
    document_id: int,
    filename: str,
    file_path: str
):
    text = extract_text(file_path)

    if not text.strip():
        return 0

    chunks = chunk_text(text)

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        f"document_{document_id}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": str(document_id),
            "filename": filename
        }
        for _ in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_documents(
    query: str,
    n_results: int = 5
):
    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    documents = results.get(
        "documents",
        [[]]
    )

    if not documents:
        return []

    return documents[0]