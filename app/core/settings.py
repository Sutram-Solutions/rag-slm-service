"""Application settings, loaded from environment variables.

Every tunable that affects retrieval quality lives here. Nothing that
affects behaviour should be a literal in application code — if a value
cannot be changed without a deploy, it will never be tuned.

Environment variables are prefixed RAG_ (e.g. RAG_DATABASE_URL).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------------------------------------------------------------- app
    environment: Literal["local", "dev", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ----------------------------------------------------------- database
    database_url: str = "postgresql+psycopg://rag_user:dev@localhost:5432/platform"

    # ------------------------------------------------------------ inbound
    # Java authenticates with one of these. Never exposed to any client.
    inbound_api_keys: list[str] = Field(default_factory=list)

    # ---------------------------------------------------------- embedding
    embedding_provider: Literal["local", "fake"] = "fake"
    embedding_model: str = "BAAI/bge-m3"  # DEFAULT for new collections only
    embedding_dimension: int = 1024  # must match the VECTOR() column
    embedding_batch_size: int = 32
    embedding_query_prefix: str = ""
    embedding_passage_prefix: str = ""

    # ----------------------------------------------------------- chunking
    chunk_target_tokens: int = 500
    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 80
    chunk_min_tokens: int = 100

    # ---------------------------------------------------------- retrieval
    default_top_k: int = 8
    max_top_k: int = 30
    candidate_multiplier: int = 8  # over-fetch before filtering
    max_candidates: int = 200
    rrf_k: int = 60
    min_score: float = 0.0
    max_per_document: int = 3
    hnsw_ef_search: int = 100

    # ----------------------------------------------------------- reranker
    rerank_enabled: bool = False  # off until measured
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    rerank_top_n: int = 40
    rerank_timeout_ms: int = 500

    # ------------------------------------------------------------- worker
    worker_poll_interval_ms: int = 2000
    worker_batch_size: int = 1

    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached accessor. Import this, not the class."""
    return Settings()
