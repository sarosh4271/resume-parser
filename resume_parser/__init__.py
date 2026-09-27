"""Resume extraction and structured parsing."""

from .chain import MAX_TEXT_LENGTH, build_chain, parse_resume
from .extractors import ExtractionError, extract_resume_text
from .models import ParsedResume
from .settings import (
    MODEL_PRESETS,
    configured_api_key,
    configured_model,
    resolve_model,
)

__all__ = [
    "ExtractionError",
    "MAX_TEXT_LENGTH",
    "ParsedResume",
    "MODEL_PRESETS",
    "build_chain",
    "configured_api_key",
    "configured_model",
    "extract_resume_text",
    "parse_resume",
    "resolve_model",
]
