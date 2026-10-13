from pathlib import Path

from app.core.config import Settings


def test_settings_accepts_legacy_rag_environment_configuration(
    monkeypatch: object,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    (tmp_path / ".env").write_text(
        "RAG_ENVIRONMENT=local\nRAG_DATABASE_URL=postgresql+psycopg://test:test@localhost/test\n",
        encoding="utf-8",
    )

    settings = Settings()  # type: ignore[call-arg]

    assert settings.environment == "development"
    assert settings.database.url.endswith("@localhost/test")
