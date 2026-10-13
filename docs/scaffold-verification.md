# Scaffold verification

Audit date: 2026-10-13

This audit checks implementation content rather than file presence. The
repository currently contains 296 Python files under `app/`, `evaluation/`,
`tests/`, and `migrations/`; 254 are zero-byte files. Empty package files and
directories are recorded as structure only, not as implemented behavior.

No existing database was reset or modified. No database integration or
migration-application check was run because no disposable PostgreSQL instance
was started during this audit.

| Requirement | Files | Implemented/Partial/Missing | Verification | Actual result | Follow-up |
| --- | --- | --- | --- | --- | --- |
| 1. Package structure and imports | `app/`, `evaluation/`, `tests/` | Partial | `python -m compileall -q app evaluation tests migrations`; import smoke test; zero-byte scan | `compileall` passed; `import app`, `app.core.config`, and `evaluation` passed; 254/296 Python files are zero bytes, so structure exists but most packages have no implementation | Implement package modules incrementally; add import/contract tests |
| 2. `pyproject.toml` and generated lockfiles | `pyproject.toml`, `requirements.lock`, `requirements-dev.lock` | Partial | `pip check`; `pip-compile --dry-run --no-index --output-file=NUL pyproject.toml`; inspect generated headers and dependency entries | `pip check` passed; both lockfiles contain pinned runtime/dev dependencies and pip-compile headers; offline regeneration failed because the package index was unavailable (`No matching distribution found for fastapi`) | Regenerate online with the documented interpreter and commit reproducible output; remove duplicate dev requirements in `pyproject.toml` |
| 3. Settings validation and secret-safe configuration | `app/core/config.py`, `app/core/settings.py`, `tests/unit/test_settings.py` | Partial | Full pytest; mypy; inspect Pydantic models and secret fields | Six tests passed; unknown `RAG_` variables are rejected by compatibility settings; API keys and compatibility DB URL use `SecretStr`; `app/core/config.py` leaves its database URL as plain `str` and does not load `.env`, so the two settings systems are inconsistent | Consolidate settings into one model, use secret-safe database URL handling throughout, and add production placeholder/startup tests |
| 4. FastAPI bootstrap, lifespan, routes, middleware, exception handlers | `app/main.py`, `app/api/routes/`, `app/api/middleware/`, `app/api/exception_handlers.py` | Missing | Inspect contents and search for `FastAPI`, `create_app`, route decorators, lifespan, and exception handlers | Target files exist but are zero bytes; no FastAPI application, `/health`, `/ready`, middleware, or central exception handlers are executable | Implement `create_app()`, lifespan, request ID middleware, safe exception envelope, health/readiness routes, and smoke tests |
| 5. Explicit missing/null/empty authorization scope | `app/security/auth.py`, `app/security/authorization.py`, `app/security/predicates.py`, route/repository files | Partial | Inspect validator and predicate code; search route/repository call sites | `AuthorizationScopeValidator` rejects `None`; tenant mismatch is checked; empty permission scope is merely represented by a value object and is not wired to return empty evidence without searching; route integration is absent | Add a request dependency and repository contract that rejects missing scope and short-circuits empty scopes before SQL |
| 6. SQL tenant/ACL/lifecycle predicates | `app/security/predicates.py`, `app/security/sql_scope.py`, `app/db/search/` | Missing | Search for SQLAlchemy `select`, joins, ACL/publication/effective/expiry predicates | The builder returns a dataclass only; SQL search files are zero bytes; no tenant, ACL, publication, effective-date, or expiry SQL predicates exist | Implement one shared SQL predicate builder and require explicit scope parameters on every repository search |
| 7. SQLAlchemy models, relationships, and constraints | `app/db/base.py`, `app/db/models/`, `app/db/repositories/` | Missing | Inspect file sizes and search for declarative `Base`, mapped classes, relationships, and constraints | Base, all model files, and repositories are zero bytes; no ORM metadata, relationships, UUID constraints, lifecycle checks, or idempotency/lease schema exist | Add metadata and models for tenants, collections, documents, versions, ACLs, revisions, chunks, embeddings, jobs, idempotency, and audit events |
| 8. Alembic configuration, revision chain, and model metadata | `alembic.ini`, `migrations/env.py`, `migrations/versions/5809ccaf2b69_baseline_chunks_table_with_hnsw_index.py` | Partial | `alembic heads`; `alembic history`; inspect `target_metadata` and revision | Chain inspection passed with one head (`5809ccaf2b69`); `migrations/env.py` sets `target_metadata = None`; only a chunks table revision exists, with HNSW created automatically and no requested full schema | Import application metadata, add reviewed forward revisions, and validate against a disposable PostgreSQL/pgvector database only |
| 9. Durable ingestion jobs, idempotency, lease ownership, recovery | `app/ingestion/`, `app/db/repositories/jobs.py`, `app/api/routes/ingestion.py` | Missing | Inspect job, repository, route, worker, idempotency, and lease files | Relevant files are zero bytes; no durable submission, status route, idempotency conflict handling, claim/heartbeat token, stale-worker recovery, or bounded worker exists | Implement short-transaction job claiming and ownership-token finalization before exposing worker success |
| 10. Retrieval implementation versus capability-unavailable placeholders | `app/retrieval/`, `app/db/search/`, `app/embeddings/`, `app/api/routes/retrieval.py` | Partial | Search for retrieval service, vector/keyword SQL, embedding calls, and capability errors | Typed domain contracts and a test fake exist; retrieval/search/service/routes are empty; no evidence search or typed capability-unavailable HTTP behavior is wired; no invented chunks are returned | Implement scoped repository and retrieval service; return explicit unavailable errors for nonempty scopes and safe empty results for empty scopes |
| 11. Evaluation metrics and unanswerable handling | `evaluation/metrics/retrieval.py`, `evaluation/schema.py`, `evaluation/loader.py`, `tests/unit/test_evaluation_metrics.py` | Implemented and verified (limited scope) | `python -m pytest`; inspect metric behavior | Six tests passed, including recall/MRR and rejection of recall for an empty relevant set; loader validates unanswerable records and abstention accuracy is separate; no full baseline/report pipeline is verified | Add dataset snapshots, nDCG only if required, report generation, and larger metric tests |
| 12. Tests, Docker, README, and runbooks | `tests/`, `docker-compose.yml`, `Dockerfile`, `README.md`, `docs/runbooks/` | Partial | Full pytest; `docker compose config --quiet`; inspect test/file contents | Six tests passed; Compose syntax passed and defines PostgreSQL/pgvector healthcheck plus persistent volume; no `Dockerfile`; `README.md` is only 18 bytes; most integration/security/contract/resilience tests are empty; runbooks are minimal | Add executable commands and operational guidance, Dockerfile/non-root entrypoint, disposable PostgreSQL integration fixtures, and meaningful security/isolation tests |

## Commands and results

| Command | Result |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pytest` | Passed: `6 passed` |
| `.\.venv\Scripts\ruff.exe check .` | Passed after the settings compatibility fix |
| `.\.venv\Scripts\ruff.exe format --check .` | Passed after the settings compatibility fix |
| `.\.venv\Scripts\mypy.exe app evaluation tests` | Passed: `Success: no issues found in 295 source files` |
| `.\.venv\Scripts\python.exe -m pip check` | Passed: `No broken requirements found` |
| `.\.venv\Scripts\python.exe -m compileall -q app evaluation tests migrations` | Passed |
| `.\.venv\Scripts\alembic.exe heads` | Passed: `5809ccaf2b69 (head)` |
| `.\.venv\Scripts\alembic.exe history` | Passed: one baseline revision |
| `docker compose config --quiet` | Passed; services were not started |
| `.\.venv\Scripts\pip-compile.exe --dry-run --no-index --output-file=NUL pyproject.toml` | Blocked: offline resolver could not find `fastapi` |

## Skipped checks and blockers

- Migration application and database integration tests were skipped because
  they require a disposable PostgreSQL 16/pgvector database. The existing
  Compose volume was not started, reset, or deleted.
- API startup and health/readiness smoke tests were skipped because
  `app/main.py` is empty and no FastAPI application exists.
- Paid model APIs and model downloads were not invoked.

The scaffold is **not production-ready**. Most requested runtime behavior is
still missing or represented only by empty package files and partial typed
contracts.
