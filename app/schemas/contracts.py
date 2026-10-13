"""Pydantic HTTP contracts; ORM objects must not cross this boundary."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RetrieveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    collection_id: UUID
    query: str = Field(min_length=1, max_length=8_000)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    version_id: UUID
    score: float


class RetrieveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str
    sources: list[SourceReference]


class IngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    collection_id: UUID
    source_path: str = Field(min_length=1, max_length=1_024)
    idempotency_key: str = Field(min_length=1, max_length=200)


class IngestionAcceptedResponse(BaseModel):
    job_id: UUID
    status: str


class IngestionStatusResponse(BaseModel):
    job_id: UUID
    status: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]
