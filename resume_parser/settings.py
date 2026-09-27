"""Safe runtime configuration helpers for the Streamlit application."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

MODEL_ID_LIMIT = 120
MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
MODEL_PRESETS = (
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-5-mini",
    "gpt-5",
    "gpt-4o-mini",
)


@dataclass(frozen=True)
class ConfiguredApiKey:
    """An API key resolved on the server without exposing it to a form widget."""

    value: str
    source: str


def configured_api_key(
    environ: Mapping[str, str], secrets: Mapping[str, object] | None = None
) -> ConfiguredApiKey | None:
    """Resolve an OpenAI key, preferring environment/.env over Streamlit secrets."""
    environment_key = environ.get("OPENAI_API_KEY", "").strip()
    if environment_key:
        return ConfiguredApiKey(environment_key, "environment or .env")

    if secrets is not None:
        secret_key = str(secrets.get("OPENAI_API_KEY", "")).strip()
        if secret_key:
            return ConfiguredApiKey(secret_key, "Streamlit secrets")
    return None


def configured_model(
    environ: Mapping[str, str], secrets: Mapping[str, object] | None = None
) -> str:
    """Resolve the optional default model without accepting invalid identifiers."""
    candidate = environ.get("OPENAI_CHAT_MODEL", "").strip()
    if not candidate and secrets is not None:
        candidate = str(secrets.get("OPENAI_CHAT_MODEL", "")).strip()
    try:
        return validate_model_id(candidate) if candidate else MODEL_PRESETS[0]
    except ValueError:
        return MODEL_PRESETS[0]


def validate_model_id(model_id: str) -> str:
    """Validate a preset or custom OpenAI model identifier."""
    model_id = model_id.strip()
    if not model_id:
        raise ValueError("Enter a custom model ID.")
    if len(model_id) > MODEL_ID_LIMIT:
        raise ValueError(f"Keep the model ID under {MODEL_ID_LIMIT} characters.")
    if not MODEL_ID_PATTERN.fullmatch(model_id):
        raise ValueError(
            "Model IDs may contain letters, numbers, dots, underscores, colons, slashes, "
            "and hyphens only."
        )
    return model_id


def resolve_model(preset: str | None, custom_model: str, source: str = "preset") -> str:
    """Return a model based on the most recently edited model control."""
    if source == "custom":
        return validate_model_id(custom_model)
    if source != "preset":
        raise ValueError("The active model source must be preset or custom.")
    if preset not in MODEL_PRESETS:
        raise ValueError("Choose a model from the preset list.")
    return preset
