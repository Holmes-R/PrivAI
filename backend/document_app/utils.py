import re
from typing import List
from docx import Document as DocxDocument

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract text from PDF, DOCX, or TXT with garbage detection."""
    file_path = str(file_path)
    text = ""

    if file_type == "pdf":
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        if _is_garbage(text):
            text = _extract_pdf_fallback(file_path)

    elif file_type == "docx":
        doc = DocxDocument(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

    return text.strip()


def _is_garbage(text: str, threshold: float = 0.4) -> bool:
    """Detect if extracted text is garbage (scanned PDF, encoding issues)."""
    if not text.strip():
        return True
    alpha = len(re.findall(r"[a-zA-Z0-9\s]", text))
    return alpha / len(text) < threshold if len(text) > 50 else False


def _extract_pdf_fallback(file_path: str) -> str:
    """Fallback: extract text via pdfminer directly with aggressive settings."""
    try:
        from pdfminer.high_level import extract_text
        return extract_text(file_path)
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
        if i >= len(words) and chunk:
            break
    return chunks