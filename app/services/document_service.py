from pathlib import Path
from docx import Document as DocxDocument
from PyPDF2 import PdfReader

def extract_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(file_path)
    if suffix in {".txt", ".md"}:
        return extract_text_file(file_path)
    if suffix == ".docx":
        return extract_docx(file_path)
    raise ValueError("Unsupported file type.")

def extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            pages.append(txt)
    return "\n".join(pages).strip()

def extract_text_file(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore").strip()

def extract_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
