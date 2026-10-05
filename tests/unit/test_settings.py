"""Settings must load, be overridable, and reject typos."""

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_settings_load_with_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "local"
    assert settings.embedding_provider == "fake"
    assert settings.embedding_dimension == 1024


def test_environment_variable_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAG_DEFAULT_TOP_K", "15")

    settings = Settings(_env_file=None)

    assert settings.default_top_k == 15


def test_unknown_setting_is_rejected_rather_than_silently_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A typo'd env var must fail loudly. Silent defaults waste afternoons."""
    monkeypatch.setenv("RAG_CHUNK_TARGET_TOKEN", "999")  # missing the S

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_reranking_is_off_by_default() -> None:
    """It stays off until the golden set says it earns its 300ms."""
    assert Settings(_env_file=None).rerank_enabled is False
