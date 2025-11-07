# document_app/utils.py
import os
from pathlib import Path
from typing import List
import PyPDF2
from docx import Document as DocxDocument
from tqdm import tqdm

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT."""
    file_path = str(file_path)
    text = ""

    if file_type == "pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"

    elif file_type == "docx":
        doc = DocxDocument(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    return text.strip()


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