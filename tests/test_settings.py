import pytest

from resume_parser.settings import (
    configured_api_key,
    configured_model,
    resolve_model,
    validate_model_id,
)


def test_environment_key_takes_precedence_over_streamlit_secret():
    result = configured_api_key(
        {"OPENAI_API_KEY": " env-key "}, {"OPENAI_API_KEY": "secret-key"}
    )
    assert result is not None
    assert result.value == "env-key"
    assert result.source == "environment or .env"


def test_streamlit_secret_is_used_without_environment_key():
    result = configured_api_key({}, {"OPENAI_API_KEY": " secret-key "})
    assert result is not None
    assert result.value == "secret-key"
    assert result.source == "Streamlit secrets"


def test_missing_key_returns_none():
    assert configured_api_key({}, {}) is None


def test_configured_model_falls_back_when_invalid():
    assert configured_model({"OPENAI_CHAT_MODEL": "bad model id"}) == "gpt-4.1-mini"


def test_resolve_custom_model():
    assert resolve_model("gpt-4.1-mini", "ft:gpt-4.1-mini:team:resume-v2", "custom") == (
        "ft:gpt-4.1-mini:team:resume-v2"
    )


def test_resolve_preset_ignores_existing_custom_value():
    assert resolve_model("gpt-5-mini", "ft:gpt-4.1-mini:team:resume-v2", "preset") == (
        "gpt-5-mini"
    )


def test_resolve_model_rejects_unknown_source():
    with pytest.raises(ValueError, match="preset or custom"):
        resolve_model("gpt-4.1-mini", "custom-model", "unknown")


@pytest.mark.parametrize("model_id", ["", "contains spaces", "gpt-4.1;$bad"])
def test_invalid_custom_model_is_rejected(model_id):
    with pytest.raises(ValueError):
        validate_model_id(model_id)
