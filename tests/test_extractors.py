from io import BytesIO

import pytest
from docx import Document

from resume_parser.extractors import ExtractionError, extract_resume_text


def test_extracts_utf8_text():
    text = "Maya Chen\nProduct Designer\nExperience building accessible onboarding workflows."
    assert extract_resume_text("resume.txt", text.encode()) == text


def test_extracts_docx_paragraphs_and_tables():
    document = Document()
    document.add_paragraph("Maya Chen — Product Designer")
    document.add_paragraph("Built onboarding systems for enterprise software teams.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Skill"
    table.cell(0, 1).text = "Figma"
    stream = BytesIO()
    document.save(stream)

    result = extract_resume_text("resume.docx", stream.getvalue())

    assert "Maya Chen" in result
    assert "Skill | Figma" in result


def test_rejects_unsupported_extension():
    with pytest.raises(ExtractionError, match="PDF, DOCX, or TXT"):
        extract_resume_text("resume.rtf", b"A resume with enough readable content to pass length.")


def test_rejects_nearly_empty_file():
    with pytest.raises(ExtractionError, match="Very little readable text"):
        extract_resume_text("resume.txt", b"Maya")


def test_rejects_non_utf8_text():
    with pytest.raises(ExtractionError, match="UTF-8"):
        extract_resume_text("resume.txt", b"\xff\xfe\xfa" * 20)

