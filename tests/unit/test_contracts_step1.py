from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.domain.contracts import (
    AuthorizationScope,
    ChunkDraft,
    DocumentVersion,
    IngestionStage,
    RetrievalFilter,
    RetrievalOutcome,
    RetrievalScore,
    ScoreType,
    SourceLocation,
)
from app.schemas.contracts import RetrieveRequest, ScoreRequest


def test_authorization_scope_distinguishes_empty_permissions_and_document_limits() -> None:
    tenant_id = uuid4()
    collection_id = uuid4()
    scope = AuthorizationScope(
        tenant_id=tenant_id,
        principal_id="principal-1",
        allowed_collection_ids=frozenset({collection_id}),
        allowed_permission_ids=frozenset(),
        allowed_document_ids=None,
        denied_document_ids=frozenset(),
    )

    assert scope.has_access_to_collection(collection_id) is False
    assert scope.allowed_document_ids is None
    document_id = uuid4()
    allowed_scope = AuthorizationScope(
        tenant_id=tenant_id,
        principal_id="principal-1",
        allowed_collection_ids=frozenset({collection_id}),
        allowed_permission_ids=frozenset({uuid4()}),
        allowed_document_ids=frozenset({document_id}),
        denied_document_ids=frozenset(),
    )
    assert allowed_scope.allows_document(collection_id, document_id) is True
    denied_scope = AuthorizationScope(
        tenant_id=tenant_id,
        principal_id="principal-1",
        allowed_collection_ids=frozenset({collection_id}),
        allowed_permission_ids=frozenset({uuid4()}),
        allowed_document_ids=frozenset({document_id}),
        denied_document_ids=frozenset({document_id}),
    )
    assert denied_scope.allows_document(collection_id, document_id) is False
    with pytest.raises(AttributeError):
        scope.allowed_collection_ids.add(uuid4())  # type: ignore[attr-defined]


def test_retrieve_request_requires_scope_and_requested_collections_are_subset() -> None:
    tenant_id = uuid4()
    allowed = uuid4()
    with pytest.raises(ValidationError):
        RetrieveRequest(
            tenant_id=tenant_id,
            collection_id=allowed,
            query="question",
            authorization_scope=None,  # type: ignore[arg-type]
        )

    with pytest.raises(ValidationError, match="subset"):
        RetrieveRequest(
            tenant_id=tenant_id,
            collection_id=allowed,
            query="question",
            authorization_scope={  # type: ignore[arg-type]
                "tenant_id": str(tenant_id),
                "principal_id": "p",
                "allowed_collection_ids": [],
                "allowed_permission_ids": [str(uuid4())],
            },
            requested_collection_ids=[str(uuid4())],  # type: ignore[arg-type]
        )


def test_contracts_validate_dates_scores_and_token_counts() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValueError):
        DocumentVersion(
            document_version_id=uuid4(),
            document_id=uuid4(),
            tenant_id=uuid4(),
            collection_id=uuid4(),
            version_number=1,
            source_reference="ref",
            source_checksum="a" * 64,
            language="en",
            effective_at=now,
            expires_at=now - timedelta(seconds=1),
            created_at=now,
            approval_status="approved",
        )

    with pytest.raises(ValueError):
        RetrievalFilter(as_of=now.replace(tzinfo=None))

    with pytest.raises(ValueError):
        ChunkDraft(
            chunk_id=uuid4(),
            tenant_id=uuid4(),
            collection_id=uuid4(),
            index_revision_id=uuid4(),
            text="source",
            embedding_text="context",
            language="en",
            embedding_input_token_count=0,
            tokenizer_revision="tok-1",
            provenance=None,  # type: ignore[arg-type]
        )


def test_retrieval_outcome_and_ingestion_stage_are_bounded() -> None:
    assert RetrievalOutcome.NO_ELIGIBLE_SOURCES.value == "no_eligible_sources"
    assert IngestionStage.QUEUED.value == "queued"


def test_offsets_pages_scores_and_top_k_are_validated() -> None:
    with pytest.raises(ValueError):
        SourceLocation(page_start=0)
    with pytest.raises(ValueError):
        SourceLocation(start_offset=4, end_offset=2)
    with pytest.raises(ValueError):
        RetrievalScore(ScoreType.RRF, float("inf"), 1)
    with pytest.raises(ValueError):
        RetrievalScore(ScoreType.RRF, 0.5, 0)
    with pytest.raises(ValidationError):
        ScoreRequest(value=float("nan"), rank=1)
