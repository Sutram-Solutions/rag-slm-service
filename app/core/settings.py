"""Compatibility settings used by the existing local development tests."""

import os
from typing import Any

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    log_level: str = "INFO"
    database_url: SecretStr = SecretStr("")
    inbound_api_keys: list[SecretStr] = Field(default_factory=list)
    embedding_provider: str = "fake"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = Field(default=1024, ge=1)
    chunk_target_tokens: int = Field(default=500, ge=1)
    chunk_max_tokens: int = Field(default=800, ge=1)
    default_top_k: int = Field(default=8, ge=1)
    candidate_multiplier: int = Field(default=8, ge=1)
    rerank_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RAG_",
        extra="forbid",
        case_sensitive=False,
    )

    def __init__(self, *, _env_file: str | None = ".env", **values: Any) -> None:
        known = {name.upper() for name in type(self).model_fields}
        unknown = sorted(
            key for key in os.environ if key.startswith("RAG_") and key[4:] not in known
        )
        if unknown:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                [
                    {
                        "type": "extra_forbidden",
                        "loc": (key,),
                        "input": os.environ[key],
                    }
                    for key in unknown
                ],
            )
        super().__init__(_env_file=_env_file, **values)
