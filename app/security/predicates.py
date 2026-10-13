"""Shared SQL predicate inputs for every scoped repository query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthorizedSearchPredicate:
    tenant_id: UUID
    collection_id: UUID
    permission_ids: frozenset[UUID]


class AuthorizedSearchPredicateBuilder:
    def build(
        self,
        *,
        tenant_id: UUID,
        collection_id: UUID,
        permission_ids: frozenset[UUID],
    ) -> AuthorizedSearchPredicate:
        if not permission_ids:
            return AuthorizedSearchPredicate(tenant_id, collection_id, permission_ids)
        return AuthorizedSearchPredicate(tenant_id, collection_id, permission_ids)
