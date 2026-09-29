import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "llama3.2"


def generate_answer(
    question: str,
    context: str
):
    prompt = f"""
You are AISoC, an AI-powered research assistant.

Answer the user's question using only the
provided research context.

If the context does not contain enough information,
clearly say that the information is not available
in the provided documents.

Do not invent facts.

Research Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        "No response generated."
    )