# RAG SLM Service Application Guide

This document explains the current application structure, the classes that
are implemented, where configuration is defined, how FastAPI and Swagger are
configured, how the database connection is created and checked, and which
scaffolded areas are not yet wired into the running application.

> **Important:** This is an implementation guide for the current repository
> state. A file existing in the scaffold does not necessarily mean that the
> corresponding feature is implemented.

## 1. Runtime entry point

The application entry point is [`app/main.py`](../app/main.py).

The application is created through the factory:

```python
from app.main import create_app

app = create_app()
```

The recommended Uvicorn command is:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

### `create_app()`

`create_app()` is responsible for:

1. Configuring structured logging.
2. Loading the validated [`Settings`](../app/core/config.py) object.
3. Creating the FastAPI application.
4. Registering the application lifespan.
5. Registering request-ID middleware.
6. Registering exception handlers.
7. Defining the `/health` and `/ready` operations endpoints.
8. Accepting an optional database manager for tests.

The function does not connect to PostgreSQL when the module is imported.
Database ownership begins during the FastAPI lifespan startup.

## 2. FastAPI lifecycle and application classes

### `ApplicationResources`

Location: [`app/main.py`](../app/main.py)

`ApplicationResources` is a dataclass containing the resources owned by one
application process.

Current resource:

| Field | Type | Purpose |
| --- | --- | --- |
| `database` | `DatabaseManager` | Runtime SQLAlchemy database manager |

Its `close()` method disposes the database engine during application shutdown.

### `RequestContextMiddleware`

Location: [`app/main.py`](../app/main.py)

This middleware:

1. Reads the incoming `X-Request-ID` header.
2. Generates a UUID request ID when the caller did not provide one.
3. Stores the ID in `request.state.request_id`.
4. Binds the ID to the Structlog context.
5. Adds the same ID to the response header.
6. Clears the Structlog context after the request.

The middleware does not log request bodies, authorization keys, database URLs,
or other secret-bearing values.

### `lifespan()`

Location: [`app/main.py`](../app/main.py)

The lifespan function runs around the entire FastAPI process lifetime.

Startup:

1. Reads `app.state.settings`.
2. Runs `Settings.validate_startup()`.
3. Uses an injected test database manager when supplied.
4. Otherwise creates a `DatabaseManager` from database settings.
5. Stores the active resources in `app.state.resources`.

Shutdown:

1. Calls `ApplicationResources.close()`.
2. Disposes the SQLAlchemy engine.
3. Clears `app.state.resources`.

Using `TestClient` as a context manager is important because it executes this
lifespan:

```python
with TestClient(create_app(test_settings, fake_database)) as client:
    response = client.get("/ready")
```

## 3. HTTP endpoints

The currently registered routes are defined directly in
[`app/main.py`](../app/main.py).

### `GET /health`

Purpose: process-level liveness check.

Response:

```json
{
  "status": "ok"
}
```

This endpoint does not access PostgreSQL. It answers whether the FastAPI
process is responding.

### `GET /ready`

Purpose: dependency readiness check.

The endpoint calls `DatabaseManager.health()`. When PostgreSQL is reachable,
it returns:

```json
{
  "status": "ready",
  "checks": {
    "configuration": "ok",
    "database": "connected"
  },
  "table_count": 4
}
```

The `table_count` value is the number of ordinary PostgreSQL base tables in
the `rag` schema. PostgreSQL system tables and views are not counted.

When the database cannot be reached, the response is HTTP `503`:

```json
{
  "status": "not_ready",
  "checks": {
    "configuration": "ok",
    "database": "unavailable"
  }
}
```

The failure response deliberately does not include the database URL,
hostname credentials, SQL statement, or exception details.

### Swagger and OpenAPI

FastAPI automatically generates OpenAPI and Swagger documentation from the
`FastAPI(...)` object in `create_app()`.

With the service running on the default port:

| URL | Purpose |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |
| `http://127.0.0.1:8000/openapi.json` | Raw OpenAPI JSON |

The current application metadata is:

| Setting | Current value |
| --- | --- |
| `title` | `RAG SLM Retrieval Service` |
| `version` | `0.1.0` |
| `lifespan` | `lifespan` from `app/main.py` |

At the current implementation stage, Swagger exposes `/health` and `/ready`.
The scaffolded ingestion and retrieval route files are not currently included
in `create_app()`, so they do not appear in Swagger until they are implemented
and registered.

## 4. Exception handling

The application registers three handlers in [`app/main.py`](../app/main.py).

### Validation errors

`_request_validation_handler()` converts request validation failures into a
safe response with code `invalid_request` and HTTP `422`.

### HTTP errors

`_http_exception_handler()` converts `HTTPException` instances into the
standard error envelope.

### Unexpected errors

`_unhandled_exception_handler()` returns a generic HTTP `500` response. It
does not expose stack traces or internal implementation details to clients.

The common error response shape is:

```json
{
  "code": "error_code",
  "message": "Safe client-facing message",
  "request_id": "request-correlation-id"
}
```

## 5. Configuration

The primary configuration model is in
[`app/core/config.py`](../app/core/config.py).

### `Settings`

`Settings` is the top-level Pydantic Settings model. It contains:

| Field | Class | Purpose |
| --- | --- | --- |
| `environment` | `str` | Environment name |
| `database` | `DatabaseSettings` | PostgreSQL connection settings |
| `auth` | `ServiceAuthSettings` | Service API-key configuration |
| `retrieval` | `RetrievalSettings` | Retrieval limits and capability flag |
| `ingestion` | `IngestionSettings` | Ingestion size limits |
| `embedding` | `EmbeddingSettings` | Model and vector configuration |

The accepted environment values are:

```text
development
test
staging
production
```

`RAG_ENVIRONMENT=local` is translated to `development` for compatibility
with the existing local `.env` file.

### `get_settings()`

`get_settings()` is an `lru_cache`-backed factory. It creates `Settings`,
validates startup constraints, and returns the cached settings object.

Caching ensures that the process uses one consistent configuration object
instead of rereading environment variables for every request.

### `DatabaseSettings`

Fields:

| Field | Default/constraint | Purpose |
| --- | --- | --- |
| `url` | Required | SQLAlchemy database URL |
| `pool_size` | Default `5`, range `1..50` | Connection-pool size |

The current repository `.env` uses the legacy variable:

```text
RAG_DATABASE_URL=postgresql+psycopg://...
```

The compatibility validator maps this to `database.url`.

The newer nested form is also supported by the Pydantic settings model:

```text
DATABASE__URL=postgresql+psycopg://...
DATABASE__POOL_SIZE=5
```

Do not commit real credentials to source control. Keep local values in
`.env`, deployment secret stores, or environment-specific secret injection.

### `ServiceAuthSettings`

`api_key` is typed as `SecretStr | None`. Pydantic prevents accidental
plaintext display in normal model representations.

Production startup rejects:

1. A missing API key.
2. An empty API key.
3. The placeholder value `change-me`.

### `RetrievalSettings`

| Field | Purpose |
| --- | --- |
| `max_top_k` | Maximum retrieval result count, default `20` |
| `capability_enabled` | Enables the configured retrieval capability |

Production startup also requires nonzero embedding dimensions when retrieval
is enabled.

### `IngestionSettings`

`max_bytes` limits the accepted ingestion payload size. The default is
10,000,000 bytes and the allowed range is 1 through 100,000,000 bytes.

### `EmbeddingSettings`

| Field | Purpose |
| --- | --- |
| `model_revision` | Embedding model revision |
| `dimensions` | Vector dimensions |
| `tokenizer_revision` | Tokenizer revision |
| `distance_metric` | Vector distance metric, default `cosine` |

## 6. Database connection implementation

The application runtime database implementation is
[`app/db/session.py`](../app/db/session.py). This is separate from the
Alembic migration connection in [`migrations/env.py`](../migrations/env.py).

### `DatabaseHealth`

`DatabaseHealth` is an immutable dataclass:

| Field | Type | Meaning |
| --- | --- | --- |
| `connected` | `bool` | Whether the health query completed |
| `table_count` | `int | None` | Number of base tables in `rag` |

### `DatabaseManager`

`DatabaseManager` owns the SQLAlchemy engine and provides:

#### `from_settings()`

Creates a SQLAlchemy engine using:

```python
create_engine(
    settings.url,
    pool_size=settings.pool_size,
    pool_pre_ping=True,
)
```

`pool_pre_ping=True` helps detect stale pooled connections before use.

#### `from_engine()`

Accepts an already-created engine. This is primarily used by tests and
allows readiness behavior to be tested without creating a real database
connection.

#### `health()`

`health()` is asynchronous from the caller's perspective, but the actual
synchronous SQLAlchemy operation runs through `asyncio.to_thread()`.

This design is intentional for Windows compatibility. The repository uses
`psycopg`, and async psycopg cannot use Windows' default
`ProactorEventLoop`. Running the short database check in a worker thread
avoids blocking the FastAPI event loop while remaining compatible with
Uvicorn on Windows.

The query is equivalent to:

```sql
SELECT count(*)
FROM information_schema.tables
WHERE table_schema = 'rag'
  AND table_type = 'BASE TABLE';
```

#### `close()`

Disposes the SQLAlchemy engine through `asyncio.to_thread()` during FastAPI
shutdown.

### Local PostgreSQL container

The local PostgreSQL service is defined in
[`docker-compose.yml`](../docker-compose.yml):

| Setting | Value |
| --- | --- |
| Image | `pgvector/pgvector:pg16` |
| Container | `rag-postgres` |
| Host port | `5433` |
| Container port | `5432` |
| Database | `platform` |
| Persistent volume | `pgdata` |

Start the existing local database without deleting its volume:

```powershell
docker compose up -d postgres
docker compose ps
```

The Compose healthcheck uses `pg_isready`.

## 7. Migration configuration

Alembic is configured through [`migrations/env.py`](../migrations/env.py).

Important behavior:

1. The migration connection string is sourced from the compatibility settings.
2. Migrations are scoped to the `rag` schema.
3. Alembic's version table is `rag.alembic_version`.
4. `include_schemas=True` is enabled.
5. Type and server-default changes are compared.
6. Windows uses a selector event-loop policy for Alembic's async migration
   path.

The current migration metadata is still:

```python
target_metadata = None
```

Therefore, ORM model autogeneration is not yet connected to Alembic. The
runtime readiness check can count tables, but this does not mean the complete
requested domain schema has been implemented.

## 8. Implemented domain and security classes

### Domain contract classes

Location: [`app/domain/contracts.py`](../app/domain/contracts.py)

These are immutable dataclasses and an enum used as typed boundaries between
future ingestion, retrieval, and authorization services.

| Class | Purpose |
| --- | --- |
| `AuthorizationScope` | Tenant, collection, and permission scope |
| `EmbeddingModelSpec` | Embedding model revision, tokenizer, dimensions, and distance metric |
| `ChunkProvenance` | Source document/version/checksum/ordinal information |
| `RetrievedChunk` | Retrieved text, provenance, and relevance score |
| `RetrievalResult` | Tuple of retrieved chunks and an outcome string |
| `IngestionJob` | Job ID, tenant, status, and creation timestamp |
| `JobStatus` | `accepted`, `running`, `blocked`, `succeeded`, and `failed` states |

### Authentication and authorization classes

Location: [`app/security/auth.py`](../app/security/auth.py)

| Class | Purpose |
| --- | --- |
| `ServiceAuthenticator` | Protocol defining service-key authentication |
| `ApiKeyAuthenticator` | Uses constant-time comparison for presented API keys |
| `AuthorizationScopeValidator` | Rejects a missing authorization scope |
| `TenantScopeValidator` | Rejects a scope whose tenant does not match the requested tenant |

### SQL predicate classes

Location: [`app/security/predicates.py`](../app/security/predicates.py)

| Class | Purpose |
| --- | --- |
| `AuthorizedSearchPredicate` | Carries tenant, collection, and permission IDs |
| `AuthorizedSearchPredicateBuilder` | Creates the typed predicate input for future repository queries |

The predicate value object exists, but it is not yet wired into implemented
SQLAlchemy repository queries. It must not be interpreted as proof that full
tenant/ACL/lifecycle filtering is complete.

## 9. HTTP schema classes

Location: [`app/schemas/contracts.py`](../app/schemas/contracts.py)

These Pydantic models define intended HTTP payload shapes:

| Class | Purpose |
| --- | --- |
| `RetrieveRequest` | Tenant, collection, query text, and bounded `top_k` |
| `SourceReference` | Document/version source and score |
| `RetrieveResponse` | Retrieval outcome and source references |
| `IngestionRequest` | Tenant, collection, source path, and idempotency key |
| `IngestionAcceptedResponse` | Accepted ingestion job ID and status |
| `IngestionStatusResponse` | Ingestion job status |
| `ErrorResponse` | Safe error code, message, and request ID |
| `ReadinessResponse` | Status and named readiness checks |

These contracts are not currently used by registered ingestion or retrieval
routes because those routes are not registered in `create_app()`.

## 10. Structured logging

Location: [`app/observability/logging.py`](../app/observability/logging.py)

`configure_logging()` configures Structlog with:

1. Context-variable merging.
2. Log levels.
3. ISO timestamps.
4. JSON rendering.

Request IDs are added by `RequestContextMiddleware` and are therefore
available to logs generated during a request.

## 11. Scaffolded but not currently wired runtime areas

The repository contains directories for the planned service architecture,
including:

- `app/api/routes/ingestion.py`
- `app/api/routes/retrieval.py`
- `app/db/models/`
- `app/db/repositories/`
- `app/db/search/`
- `app/ingestion/`
- `app/retrieval/`
- `app/embeddings/`
- `app/storage/`
- `app/operations/`
- `evaluation/`

These locations describe the intended architecture, but they should only be
called implemented after their functions/classes have executable behavior,
tests, and registration in the application. At the current state:

- `/health` and `/ready` are the active HTTP routes.
- Retrieval is not a working evidence-search API.
- Ingestion is not a durable worker API.
- ORM metadata is not connected to Alembic autogeneration.
- The authorization predicate object is not yet enforced by repository SQL.

## 12. Verification commands

Run the following checks from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
.\.venv\Scripts\python.exe -m mypy app tests
```

To verify the running API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/ready`
- `http://127.0.0.1:8000/docs`

Do not reset the existing PostgreSQL database or delete the `pgdata` volume
when performing local verification.
