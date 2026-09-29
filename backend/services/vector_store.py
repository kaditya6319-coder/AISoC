import chromadb


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="aisoc_documents"
)


def add_documents(
    documents: list[str],
    embeddings: list[list[float]],
    ids: list[str],
    metadatas: list[dict]
):
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


def search_documents(
    embedding: list[float],
    n_results: int = 5
):
    return collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )