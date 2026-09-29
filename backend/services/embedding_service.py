from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def generate_embeddings(texts: list[str]):
    return model.encode(
        texts,
        convert_to_numpy=True
    ).tolist()


def generate_embedding(text: str):
    return model.encode(
        text,
        convert_to_numpy=True
    ).tolist()