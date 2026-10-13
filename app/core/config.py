"""Validated configuration for the new ingestion/retrieval foundation."""

from collections.abc import Callable
from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    url: str
    pool_size: int = Field(default=5, ge=1, le=50)

    model_config = SettingsConfigDict(extra="forbid")


class ServiceAuthSettings(BaseSettings):
    api_key: SecretStr | None = None

    model_config = SettingsConfigDict(extra="forbid")


class RetrievalSettings(BaseSettings):
    max_top_k: int = Field(default=20, ge=1, le=100)
    capability_enabled: bool = False

    model_config = SettingsConfigDict(extra="forbid")


class IngestionSettings(BaseSettings):
    max_bytes: int = Field(
        default=10_000_000,
        ge=1,
        le=100_000_000,
    )

    model_config = SettingsConfigDict(extra="forbid")


class EmbeddingSettings(BaseSettings):
    model_revision: str = "unconfigured"
    dimensions: int = Field(default=0, ge=0, le=16_384)
    tokenizer_revision: str = "unconfigured"
    distance_metric: str = "cosine"

    model_config = SettingsConfigDict(extra="forbid")


class Settings(BaseSettings):
    environment: str = Field(default="development", validation_alias="APP_ENVIRONMENT")
    database: DatabaseSettings
    auth: ServiceAuthSettings = ServiceAuthSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    ingestion: IngestionSettings = IngestionSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="forbid",
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def adapt_legacy_environment(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        data = dict(values)
        legacy: dict[str, tuple[str, Callable[[str], object]]] = {
            "RAG_ENVIRONMENT": (
                "environment",
                lambda value: "development" if value == "local" else value,
            ),
            "RAG_DATABASE_URL": ("database.url", str),
            "RAG_DEFAULT_TOP_K": ("retrieval.max_top_k", int),
            "RAG_RERANK_ENABLED": ("retrieval.capability_enabled", lambda value: value == "true"),
            "RAG_EMBEDDING_MODEL": ("embedding.model_revision", str),
            "RAG_EMBEDDING_DIMENSION": ("embedding.dimensions", int),
        }
        for key, (path, converter) in legacy.items():
            source_key = next(
                (candidate for candidate in data if candidate.upper() == key),
                None,
            )
            if source_key is None:
                continue
            value = converter(data.pop(source_key))
            section, field = path.split(".", maxsplit=1) if "." in path else ("", path)
            if section:
                existing = data.get(section)
                if existing is None:
                    data[section] = {field: value}
                elif isinstance(existing, dict):
                    existing.setdefault(field, value)
            else:
                data.setdefault(field, value)

        for key in (
            "RAG_LOG_LEVEL",
            "RAG_INBOUND_API_KEYS",
            "RAG_EMBEDDING_PROVIDER",
            "RAG_CHUNK_TARGET_TOKENS",
            "RAG_CHUNK_MAX_TOKENS",
            "RAG_CANDIDATE_MULTIPLIER",
        ):
            for source_key in tuple(data):
                if source_key.upper() == key:
                    data.pop(source_key)
        return data

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "test", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"environment must be one of {sorted(allowed)}")
        return value

    def validate_startup(self) -> None:
        if self.environment == "production":
            if self.auth.api_key is None or self.auth.api_key.get_secret_value() in {
                "",
                "change-me",
            }:
                raise ValueError("production requires a non-placeholder SERVICE_API_KEY")
            if self.retrieval.capability_enabled and self.embedding.dimensions == 0:
                raise ValueError("enabled retrieval requires EMBEDDING_DIMENSIONS")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()  # type: ignore[call-arg]
    settings.validate_startup()
    return settings
