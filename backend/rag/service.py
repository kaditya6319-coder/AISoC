import os
import re

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="aisoc_documents"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pages(file_path: str):
    """
    Extract PDF text page-by-page.

    Returns:
        [
            {
                "page": 1,
                "text": "..."
            },
            ...
        ]
    """

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if not text:
            continue

        text = clean_text(text)

        if not text:
            continue

        pages.append(
            {
                "page": page_number,
                "text": text
            }
        )

    return pages


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:

    # Remove excessive whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Normalize excessive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Fix common PDF hyphenation
    text = re.sub(
        r"-\n",
        "",
        text
    )

    return text.strip()


# ============================================================
# REMOVE BIBLIOGRAPHY NOISE
# ============================================================

def is_reference_chunk(text: str) -> bool:

    lowered = text.lower()

    reference_signals = [
        "references",
        "proceedings of the",
        "arxiv preprint",
        "technical report",
        "in proceedings",
        "ieee computer society",
        "acm sigkdd",
        "pages ",
        "vol."
    ]

    score = sum(
        1
        for signal in reference_signals
        if signal in lowered
    )

    # Strong indication of bibliography
    if (
        score >= 3
        and (
            "[1]" in text
            or "[2]" in text
            or "[3]" in text
        )
    ):
        return True

    return False


# ============================================================
# CHUNK TEXT
# ============================================================

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200
):

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start += (
            chunk_size - overlap
        )

    return chunks


# ============================================================
# INDEX DOCUMENT
# ============================================================

def index_document(
    document_id: int,
    filename: str,
    file_path: str
):

    pages = extract_pages(
        file_path
    )

    if not pages:
        return 0

    all_chunks = []

    # --------------------------------------------------------
    # CREATE PAGE-AWARE CHUNKS
    # --------------------------------------------------------

    for page_data in pages:

        page_number = page_data["page"]
        page_text = page_data["text"]

        chunks = chunk_text(
            page_text
        )

        for chunk_index, chunk in enumerate(
            chunks
        ):

            all_chunks.append(
                {
                    "document": chunk,
                    "page": page_number,
                    "chunk_index": chunk_index
                }
            )

    if not all_chunks:
        return 0

    # --------------------------------------------------------
    # DELETE OLD CHUNKS FOR THIS DOCUMENT
    # --------------------------------------------------------

    try:

        collection.delete(
            where={
                "document_id": str(document_id)
            }
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # EMBEDDINGS
    # --------------------------------------------------------

    documents = [
        item["document"]
        for item in all_chunks
    ]

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    # --------------------------------------------------------
    # IDS
    # --------------------------------------------------------

    ids = [
        (
            f"document_{document_id}"
            f"_page_{item['page']}"
            f"_chunk_{item['chunk_index']}"
        )
        for item in all_chunks
    ]

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    metadatas = [
        {
            "document_id": str(document_id),
            "filename": filename,
            "page": item["page"],
            "chunk_index": item["chunk_index"]
        }
        for item in all_chunks
    ]

    # --------------------------------------------------------
    # STORE IN CHROMADB
    # --------------------------------------------------------

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(all_chunks)


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

def search_documents(
    query: str,
    document_id: int,
    n_results: int = 5
):

    query = query.strip()

    if not query:
        return []

    # --------------------------------------------------------
    # SEARCH MORE CANDIDATES
    # --------------------------------------------------------

    candidate_count = max(
        n_results * 4,
        20
    )

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=candidate_count,
        where={
            "document_id": str(document_id)
        },
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )

    metadatas = results.get(
        "metadatas",
        [[]]
    )

    distances = results.get(
        "distances",
        [[]]
    )

    if not documents or not documents[0]:
        return []

    documents = documents[0]
    metadatas = (
        metadatas[0]
        if metadatas
        else []
    )

    distances = (
        distances[0]
        if distances
        else []
    )

    candidates = []

    # --------------------------------------------------------
    # BUILD CANDIDATES
    # --------------------------------------------------------

    for index, document in enumerate(
        documents
    ):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else 1.0
        )

        page = int(
            metadata.get(
                "page",
                999
            )
        )

        # Skip obvious bibliography chunks
        reference_chunk = is_reference_chunk(
            document
        )

        # Chroma distance:
        # smaller = more similar
        #
        # Convert it into a similarity-like
        # score for ranking.
        similarity = 1.0 - float(
            distance
        )

        # ----------------------------------------------------
        # RANKING BOOSTS
        # ----------------------------------------------------

        score = similarity

        # Questions about the paper itself are
        # usually answered in the first pages.
        if page <= 2:
            score += 0.12

        elif page == 3:
            score += 0.05

        # Penalize bibliography
        if reference_chunk:
            score -= 0.25

        # ----------------------------------------------------
        # IMPORTANT KEYWORDS
        # ----------------------------------------------------

        lowered_query = query.lower()
        lowered_document = document.lower()

        important_terms = [
            "main topic",
            "topic",
            "abstract",
            "research paper",
            "paper about",
            "purpose",
            "objective",
            "propose",
            "proposed",
            "aitest",
            "automated testing",
            "ai model"
        ]

        if any(
            term in lowered_query
            for term in important_terms
        ):

            if any(
                term in lowered_document
                for term in [
                    "abstract",
                    "automated testing",
                    "ai models",
                    "aitest",
                    "black-box",
                    "testing framework"
                ]
            ):

                score += 0.15

        candidates.append(
            {
                "document": document,
                "document_id": str(
                    document_id
                ),
                "filename": metadata.get(
                    "filename",
                    ""
                ),
                "page": page,
                "chunk_index": metadata.get(
                    "chunk_index",
                    0
                ),
                "distance": distance,
                "score": score
            }
        )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATE / VERY SIMILAR TEXT
    # --------------------------------------------------------

    selected = []

    for candidate in candidates:

        current_text = candidate[
            "document"
        ].lower()

        duplicate = False

        for existing in selected:

            existing_text = existing[
                "document"
            ].lower()

            # Simple overlap check
            current_words = set(
                current_text.split()
            )

            existing_words = set(
                existing_text.split()
            )

            if not current_words:
                continue

            overlap = (
                len(
                    current_words
                    & existing_words
                )
                /
                len(current_words)
            )

            if overlap > 0.80:
                duplicate = True
                break

        if not duplicate:
            selected.append(
                candidate
            )

        if len(selected) >= n_results:
            break

    return selected