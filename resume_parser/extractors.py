"""Local text extraction for supported resume formats."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_PDF_PAGES = 40
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class ExtractionError(ValueError):
    """Raised when a resume cannot be safely converted to text."""


def _extract_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
    except Exception as error:
        message = "The PDF could not be opened. It may be damaged or encrypted."
        raise ExtractionError(message) from error

    if reader.is_encrypted:
        raise ExtractionError("Password-protected PDFs are not supported.")
    if len(reader.pages) > MAX_PDF_PAGES:
        raise ExtractionError(f"PDFs are limited to {MAX_PDF_PAGES} pages.")

    pages: list[str] = []
    try:
        for page in reader.pages:
            text = page.extract_text(extraction_mode="layout") or ""
            pages.append(text.strip())
    except Exception as error:
        raise ExtractionError("Text could not be extracted from this PDF.") from error
    return "\n\n".join(page for page in pages if page)


def _extract_docx(data: bytes) -> str:
    try:
        document = Document(BytesIO(data))
    except Exception as error:
        raise ExtractionError("The DOCX file could not be opened.") from error

    blocks: list[str] = [paragraph.text.strip() for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                blocks.append(" | ".join(cells))
    return "\n".join(block for block in blocks if block)


def _extract_txt(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ExtractionError("TXT resumes must use UTF-8 encoding.") from error


def extract_resume_text(filename: str, data: bytes) -> str:
    """Extract normalized text from a PDF, DOCX, or UTF-8 TXT upload."""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ExtractionError("Upload a PDF, DOCX, or TXT resume.")
    if not data:
        raise ExtractionError("The uploaded file is empty.")
    if len(data) > MAX_FILE_BYTES:
        raise ExtractionError("The resume must be 8 MB or smaller.")

    if extension == ".pdf":
        text = _extract_pdf(data)
    elif extension == ".docx":
        text = _extract_docx(data)
    else:
        text = _extract_txt(data)

    text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if len(text) < 40:
        raise ExtractionError(
            "Very little readable text was found. If this is a scanned PDF, run OCR first."
        )
    return text
