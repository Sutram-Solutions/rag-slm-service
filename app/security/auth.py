"""Replaceable service authentication and scope validation."""

import secrets
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.domain.contracts import AuthorizationScope


class ServiceAuthenticator(Protocol):
    def authenticate(self, presented_key: str | None) -> bool: ...


@dataclass(frozen=True)
class ApiKeyAuthenticator:
    expected_key: str

    def authenticate(self, presented_key: str | None) -> bool:
        return presented_key is not None and secrets.compare_digest(
            presented_key,
            self.expected_key,
        )


class AuthorizationScopeValidator:
    def validate(self, scope: AuthorizationScope | None) -> AuthorizationScope:
        if scope is None:
            raise ValueError("authorization scope is required")
        return scope


class TenantScopeValidator:
    def validate(self, scope: AuthorizationScope, tenant_id: UUID) -> None:
        if scope.tenant_id != tenant_id:
            raise ValueError("tenant scope mismatch")
