from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(path)

    elif extension == ".docx":
        return extract_docx_text(path)

    elif extension == ".txt":
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_docx_text(path: Path) -> str:
    document = DocxDocument(str(path))

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)