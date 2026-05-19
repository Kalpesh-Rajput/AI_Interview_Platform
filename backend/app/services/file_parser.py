import io
from pathlib import Path

from docx import Document
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Allowed: PDF, DOC, DOCX, TXT."
        )
    return ext


def extract_text_from_bytes(content: bytes, filename: str) -> str:
    ext = validate_extension(filename)

    if ext == ".txt":
        return content.decode("utf-8", errors="replace").strip()

    if ext == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError("Could not extract text from PDF. The file may be scanned or empty.")
        return text

    if ext in {".doc", ".docx"}:
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs).strip()
        if not text:
            raise ValueError("Could not extract text from document.")
        return text

    raise ValueError(f"Unsupported file type: {ext}")
