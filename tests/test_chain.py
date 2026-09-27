import pytest

from resume_parser.chain import MAX_TEXT_LENGTH, parse_resume, validate_resume_text
from resume_parser.models import ContactInfo, ParsedResume


class FakeChain:
    def __init__(self, result):
        self.result = result
        self.payload = None

    def invoke(self, payload):
        self.payload = payload
        return self.result


RESUME_TEXT = "Maya Chen is a product designer with experience building onboarding workflows."


def test_validate_resume_text_strips_whitespace():
    assert validate_resume_text(f"  {RESUME_TEXT}  ") == RESUME_TEXT


def test_validate_resume_text_rejects_too_long_content():
    with pytest.raises(ValueError, match="too long"):
        validate_resume_text("x" * (MAX_TEXT_LENGTH + 1))


def test_parse_resume_invokes_chain_and_returns_model():
    expected = ParsedResume(contact=ContactInfo(full_name="Maya Chen"), skills=["Figma"])
    chain = FakeChain(expected)

    result = parse_resume(chain, RESUME_TEXT)

    assert result == expected
    assert chain.payload == {"resume_text": RESUME_TEXT}


def test_parse_resume_validates_dictionary_result():
    chain = FakeChain({"contact": {"full_name": "Maya Chen"}, "skills": ["Figma"]})
    result = parse_resume(chain, RESUME_TEXT)
    assert isinstance(result, ParsedResume)
    assert result.contact.full_name == "Maya Chen"

