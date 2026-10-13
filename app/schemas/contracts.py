"""Strict Pydantic v2 HTTP contracts; ORM objects must not cross this boundary."""

from datetime import datetime
from math import isfinite
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AuthorizationScopeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: UUID
    principal_id: str = Field(min_length=1, max_length=200)
    allowed_collection_ids: frozenset[UUID]
    allowed_permission_ids: frozenset[UUID]
    allowed_document_ids: frozenset[UUID] | None = None
    denied_document_ids: frozenset[UUID] = frozenset()


class RetrievalFilterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: frozenset[str] = frozenset()
    languages: frozenset[str] = frozenset()
    as_of: datetime | None = None

    @field_validator("as_of")
    @classmethod
    def require_aware_as_of(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("as_of must be timezone-aware")
        return value


class RetrieveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    collection_id: UUID
    query: str = Field(min_length=1, max_length=8_000)
    authorization_scope: AuthorizationScopeRequest
    requested_collection_ids: frozenset[UUID] | None = None
    top_k: int = Field(default=5, ge=1, le=100)
    filters: RetrievalFilterRequest = Field(default_factory=RetrievalFilterRequest)

    @field_validator("query")
    @classmethod
    def reject_blank_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be blank")
        return value

    @model_validator(mode="after")
    def validate_scope_and_collections(self) -> "RetrieveRequest":
        if self.authorization_scope.tenant_id != self.tenant_id:
            raise ValueError("authorization scope tenant does not match request tenant")
        requested = self.requested_collection_ids
        if requested is not None and not requested.issubset(
            self.authorization_scope.allowed_collection_ids
        ):
            raise ValueError("requested collection IDs must be a subset of allowed collection IDs")
        if self.collection_id not in self.authorization_scope.allowed_collection_ids:
            raise ValueError("collection_id is outside the authorization scope")
        return self

    def validate_top_k(self, max_top_k: int) -> "RetrieveRequest":
        if self.top_k > max_top_k:
            raise ValueError(f"top_k must not exceed configured maximum {max_top_k}")
        return self


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    document_version_id: UUID
    chunk_id: UUID
    index_revision_id: UUID
    document_title: str | None = None
    source_locations: tuple[dict[str, object], ...] = ()


class RetrieveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str
    evidence_chunks: list[dict[str, object]] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)
    request_id: str
    configuration_revision: str
    degraded_reasons: tuple[str, ...] = ()


class IngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    collection_id: UUID
    document_version_id: UUID
    expected_checksum: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    configuration_revision: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=200)
    authorization_scope: AuthorizationScopeRequest

    @model_validator(mode="after")
    def validate_tenant_scope(self) -> "IngestionRequest":
        if self.authorization_scope.tenant_id != self.tenant_id:
            raise ValueError("authorization scope tenant does not match request tenant")
        if self.collection_id not in self.authorization_scope.allowed_collection_ids:
            raise ValueError("collection_id is outside the authorization scope")
        return self


class IngestionAcceptedResponse(BaseModel):
    job_id: UUID
    status: str
    request_id: str


class IngestionStatusResponse(BaseModel):
    job_id: UUID
    status: str
    stage: str
    attempt_count: int = Field(ge=0)
    created_at: datetime
    updated_at: datetime
    safe_error_code: str | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    request_id: str
    retryable: bool = False


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]
    table_count: int | None = Field(default=None, ge=0)


class ScoreRequest(BaseModel):
    value: float
    rank: int = Field(ge=1)

    @field_validator("value")
    @classmethod
    def require_finite_value(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("score must be finite")
        return value
