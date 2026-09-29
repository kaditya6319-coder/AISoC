from services.embedding_service import generate_embedding
from services.vector_store import search_documents
import ollama


def retrieve_context(question: str, n_results: int = 5):
    question_embedding = generate_embedding(question)

    results = search_documents(
        question_embedding,
        n_results
    )

    documents = results.get("documents", [[]])[0]

    return documents


def generate_answer(question: str):
    context_documents = retrieve_context(question)

    context = "\n\n".join(context_documents)

    prompt = f"""
You are AISoC, an AI-powered research assistant.

Answer the user's question using the provided research context.

If the answer cannot be found in the context, clearly say that
the information is not available in the provided documents.

Research Context:
{context}

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]