"""Immutable domain contracts shared by ingestion, retrieval, and authorization."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import isfinite
from uuid import UUID


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _require_checksum(value: str) -> None:
    if len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
        raise ValueError("source_checksum must be a 64-character hexadecimal checksum")


@dataclass(frozen=True)
class Document:
    document_id: UUID
    tenant_id: UUID
    collection_id: UUID
    title: str
    category: str


@dataclass(frozen=True)
class DocumentVersion:
    document_version_id: UUID
    document_id: UUID
    tenant_id: UUID
    collection_id: UUID
    version_number: int
    source_reference: str
    source_checksum: str
    language: str
    effective_at: datetime
    expires_at: datetime | None
    created_at: datetime
    approval_status: str
    rights_reference: str | None = None

    def __post_init__(self) -> None:
        if self.version_number < 1:
            raise ValueError("version_number must be positive")
        _require_checksum(self.source_checksum)
        _require_aware(self.effective_at, "effective_at")
        _require_aware(self.created_at, "created_at")
        if self.expires_at is not None:
            _require_aware(self.expires_at, "expires_at")
            if self.expires_at <= self.effective_at:
                raise ValueError("expires_at must be later than effective_at")


@dataclass(frozen=True)
class SourceLocation:
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple[str, ...] = ()
    start_offset: int | None = None
    end_offset: int | None = None
    offset_coordinate_system: str = "original_text"

    def __post_init__(self) -> None:
        if self.page_start is not None and self.page_start < 1:
            raise ValueError("page_start must be one-based and positive")
        if self.page_end is not None and self.page_end < 1:
            raise ValueError("page_end must be one-based and positive")
        if (
            self.page_start is not None
            and self.page_end is not None
            and self.page_end < self.page_start
        ):
            raise ValueError("page_end must not precede page_start")
        if (self.start_offset is None) != (self.end_offset is None):
            raise ValueError("start_offset and end_offset must be provided together")
        if self.start_offset is not None and self.start_offset < 0:
            raise ValueError("start_offset must not be negative")
        if self.end_offset is not None and self.end_offset < 0:
            raise ValueError("end_offset must not be negative")
        if (
            self.start_offset is not None
            and self.end_offset is not None
            and self.end_offset < self.start_offset
        ):
            raise ValueError("end_offset must not precede start_offset")


@dataclass(frozen=True)
class TextBlock:
    block_id: UUID
    ordinal: int
    text: str
    block_type: str
    source_location: SourceLocation

    def __post_init__(self) -> None:
        if self.ordinal < 0:
            raise ValueError("block ordinal must not be negative")
        if not self.text.strip():
            raise ValueError("text must not be blank")


@dataclass(frozen=True)
class ExtractedDocument:
    document_version_id: UUID
    source_checksum: str
    extraction_revision: str
    blocks: tuple[TextBlock, ...]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_checksum(self.source_checksum)


@dataclass(frozen=True)
class ChunkProvenance:
    document_id: UUID
    document_version_id: UUID
    source_checksum: str
    chunk_ordinal: int
    source_locations: tuple[SourceLocation, ...]
    extraction_revision: str
    normalization_revision: str
    chunking_revision: str

    def __post_init__(self) -> None:
        _require_checksum(self.source_checksum)
        if self.chunk_ordinal < 0:
            raise ValueError("chunk_ordinal must not be negative")


@dataclass(frozen=True)
class ChunkDraft:
    chunk_id: UUID
    tenant_id: UUID
    collection_id: UUID
    index_revision_id: UUID
    text: str
    embedding_text: str
    language: str
    embedding_input_token_count: int
    tokenizer_revision: str
    provenance: ChunkProvenance

    def __post_init__(self) -> None:
        if not self.text.strip() or not self.embedding_text.strip():
            raise ValueError("text and embedding_text must not be blank")
        if self.embedding_input_token_count < 1:
            raise ValueError("embedding_input_token_count must be positive")


@dataclass(frozen=True)
class EmbeddingModelSpec:
    model_id: str
    model_revision: str
    tokenizer_id: str
    tokenizer_revision: str
    dimensions: int
    distance_metric: str
    normalization_policy: str
    preprocessing_revision: str
    query_prefix: str
    document_prefix: str
    max_input_tokens: int

    def __post_init__(self) -> None:
        if self.dimensions < 1:
            raise ValueError("dimensions must be positive")
        if self.max_input_tokens < 1:
            raise ValueError("max_input_tokens must be positive")


@dataclass(frozen=True)
class CollectionConfiguration:
    collection_id: UUID
    tenant_id: UUID
    configuration_revision: str
    embedding_spec: EmbeddingModelSpec
    chunking_revision: str
    retrieval_policy_revision: str
    supported_languages: frozenset[str]


@dataclass(frozen=True)
class AuthorizationScope:
    tenant_id: UUID
    principal_id: str
    allowed_collection_ids: frozenset[UUID]
    allowed_permission_ids: frozenset[UUID]
    allowed_document_ids: frozenset[UUID] | None = None
    denied_document_ids: frozenset[UUID] = frozenset()

    def has_access_to_collection(self, collection_id: UUID) -> bool:
        return collection_id in self.allowed_collection_ids and bool(self.allowed_permission_ids)

    def allows_document(self, collection_id: UUID, document_id: UUID) -> bool:
        if not self.has_access_to_collection(collection_id):
            return False
        if document_id in self.denied_document_ids:
            return False
        return self.allowed_document_ids is None or document_id in self.allowed_document_ids


@dataclass(frozen=True)
class RetrievalFilter:
    categories: frozenset[str] = frozenset()
    languages: frozenset[str] = frozenset()
    as_of: datetime | None = None

    def __post_init__(self) -> None:
        if self.as_of is not None:
            _require_aware(self.as_of, "as_of")


class ScoreType(StrEnum):
    COSINE_SIMILARITY = "cosine_similarity"
    COSINE_DISTANCE = "cosine_distance"
    RRF = "rrf"
    RERANKER = "reranker"


@dataclass(frozen=True)
class RetrievalScore:
    score_type: ScoreType
    value: float
    rank: int

    def __post_init__(self) -> None:
        if not isfinite(self.value):
            raise ValueError("score value must be finite")
        if self.rank < 1:
            raise ValueError("rank must be positive")


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: UUID
    tenant_id: UUID
    collection_id: UUID
    index_revision_id: UUID
    text: str
    provenance: ChunkProvenance
    ranking_scores: tuple[RetrievalScore, ...]


class RetrievalOutcome(StrEnum):
    RESULTS = "results"
    NO_ELIGIBLE_SOURCES = "no_eligible_sources"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class RetrievalResult:
    chunks: tuple[RetrievedChunk, ...]
    outcome: RetrievalOutcome
    request_id: str
    configuration_revision: str
    degraded_reasons: tuple[str, ...] = ()


class JobStatus(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class IngestionStage(StrEnum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    PUBLISHING = "publishing"
    COMPLETE = "complete"


@dataclass(frozen=True)
class IngestionJob:
    job_id: UUID
    tenant_id: UUID
    collection_id: UUID
    document_version_id: UUID
    status: JobStatus
    stage: IngestionStage
    attempt_count: int
    created_at: datetime
    updated_at: datetime
    safe_error_code: str | None = None

    def __post_init__(self) -> None:
        if self.attempt_count < 0:
            raise ValueError("attempt_count must not be negative")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")
