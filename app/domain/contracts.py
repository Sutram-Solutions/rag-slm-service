"""Typed domain values for ingestion and retrieval."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


@dataclass(frozen=True)
class AuthorizationScope:
    tenant_id: UUID
    collection_ids: frozenset[UUID]
    permission_ids: frozenset[UUID]


@dataclass(frozen=True)
class EmbeddingModelSpec:
    model_revision: str
    tokenizer_revision: str
    dimensions: int
    distance_metric: str


@dataclass(frozen=True)
class ChunkProvenance:
    document_id: UUID
    version_id: UUID
    source_checksum: str
    ordinal: int


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    text: str
    provenance: ChunkProvenance
    score: float


@dataclass(frozen=True)
class RetrievalResult:
    chunks: tuple[RetrievedChunk, ...]
    outcome: str


class JobStatus(StrEnum):
    ACCEPTED = "accepted"
    RUNNING = "running"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class IngestionJob:
    job_id: UUID
    tenant_id: UUID
    status: JobStatus
    created_at: datetime
