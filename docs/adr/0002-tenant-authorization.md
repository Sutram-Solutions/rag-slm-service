# ADR 0002: Tenant authorization

Every request-serving repository method must receive an explicit scope.
Missing scope is rejected; an empty permission set produces empty evidence
without searching. Tenant, collection, ACL, publication, and effective-date
predicates are shared rather than reimplemented per query.
