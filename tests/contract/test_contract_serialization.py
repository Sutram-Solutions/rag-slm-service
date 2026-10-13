from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.contracts import (
    AuthorizationScopeRequest,
    ErrorResponse,
    ReadinessResponse,
    RetrieveRequest,
)


def test_scoped_retrieval_request_serializes_with_explicit_empty_permissions() -> None:
    tenant_id = uuid4()
    collection_id = uuid4()
    request = RetrieveRequest(
        tenant_id=tenant_id,
        collection_id=collection_id,
        query="What is photosynthesis?",
        authorization_scope=AuthorizationScopeRequest(
            tenant_id=tenant_id,
            principal_id="training-user",
            allowed_collection_ids=frozenset({collection_id}),
            allowed_permission_ids=frozenset(),
        ),
    )

    payload = request.model_dump(mode="json")

    assert payload["authorization_scope"]["allowed_permission_ids"] == []
    assert payload["top_k"] == 5


def test_readiness_and_error_contracts_remain_safe_and_compatible() -> None:
    readiness = ReadinessResponse(
        status="ready",
        checks={"database": "connected"},
        table_count=4,
    )
    error = ErrorResponse(
        code="database_unavailable",
        message="Database is unavailable",
        request_id="request-1",
        retryable=True,
    )

    assert readiness.model_dump() == {
        "status": "ready",
        "checks": {"database": "connected"},
        "table_count": 4,
    }
    assert "password" not in error.model_dump_json().lower()
    assert datetime.now(UTC).tzinfo is not None
