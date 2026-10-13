# Step 1: Shared Domain and API Contracts

This document describes the contract layer implemented for the reusable
Python RAG service. It defines typed internal values and strict external API
payloads. It does **not** implement ORM tables, SQL repositories, extraction,
embedding execution, workers, retrieval, answer generation, or new routes.

## Ownership and service boundary

- Java remains responsible for user authentication and permission decisions.
- Java supplies a trusted authorization scope to Python.
- Python validates the scope and will enforce it in future SQL repositories.
- Python returns evidence and provenance.
- Java remains responsible for generating user-facing answers.
- A tenant or principal identifier in a request is not authentication by
  itself.

## Internal domain contracts

Implemented in [`app/domain/contracts.py`](../app/domain/contracts.py).
Internal collections use tuples or frozensets and the dataclasses are frozen.
This prevents accidental mutation after validation.

### Documents and source content

| Model | Purpose |
| --- | --- |
| `Document` | Stable document identity and tenant/collection ownership |
| `DocumentVersion` | Immutable source version, checksum, language, approval, and lifecycle dates |
| `SourceLocation` | Page, section, and text-offset provenance |
| `TextBlock` | Extracted source block with an ordinal and location |
| `ExtractedDocument` | Extraction output and extraction warnings |

`SourceLocation` uses one-based page numbers. Pages are optional and must not
be invented for DOCX or plain-text sources. Offsets use
`offset_coordinate_system`, which defaults to `original_text`; future
normalization code must explicitly change the coordinate system when offsets
refer to normalized text.

Document versions are immutable values. `expires_at`, when supplied, must be
later than `effective_at`. Checksums must be 64-character hexadecimal values.

### Chunks and embeddings

| Model | Purpose |
| --- | --- |
| `ChunkProvenance` | Connects a chunk to its immutable source version and processing revisions |
| `ChunkDraft` | Separates original chunk text from `embedding_text` |
| `EmbeddingModelSpec` | Identifies model/tokenizer revisions and vector compatibility |
| `CollectionConfiguration` | Binds collection policy and embedding configuration |

`text` is the source-facing text. `embedding_text` is the exact text intended
for embedding and must remain a separate field. The contracts do not
calculate tokenizer counts; callers supply and validate the count.

Embedding dimensions and maximum input tokens must be positive. Different
model revisions, tokenizer revisions, dimensions, distance metrics, or
preprocessing revisions must not be mixed by future indexing code.

### Authorization semantics

`AuthorizationScope` contains:

- `tenant_id`
- `principal_id`
- `allowed_collection_ids`
- `allowed_permission_ids`
- optional `allowed_document_ids`
- `denied_document_ids`

The intended access rule is:

```text
tenant match
AND collection is allowed
AND at least one explicit permission is allowed
AND optional document allow-list matches
AND document is not denied
```

Specific semantics:

- Missing or null scope is invalid at the API boundary.
- Empty `allowed_collection_ids` means no access.
- Empty `allowed_permission_ids` means no access.
- `allowed_document_ids=None` means no additional document restriction.
- `allowed_document_ids=()` means no documents are allowed.
- Denied document IDs override allowed document IDs.
- Requested filters can narrow results but cannot expand authorization.
- A principal ID or tenant ID does not authenticate the caller.

The current internal helper `has_access_to_collection()` represents the
collection-plus-permission portion of this rule. Future repository code must
also enforce tenant, document, lifecycle, and ACL predicates in SQL.

### Retrieval

| Model | Purpose |
| --- | --- |
| `RetrievalFilter` | Category, language, and historical `as_of` restrictions |
| `RetrievalScore` | Typed ranking score with score kind and positive rank |
| `RetrievedChunk` | Evidence chunk with tenant/collection/index revision and provenance |
| `RetrievalOutcome` | `results`, `no_eligible_sources`, or `insufficient_evidence` |
| `RetrievalResult` | Evidence, primary outcome, request ID, configuration revision, and degradation reasons |

Scores are ranking values, not confidence probabilities. The supported score
types distinguish cosine similarity, cosine distance, reciprocal-rank fusion,
and reranker scores. Scores must be finite and ranks must be positive.

Degradation is represented by `degraded_reasons`; it does not replace the
primary retrieval outcome.

### Ingestion jobs

`IngestionJob` contains tenant, collection, document-version, status, stage,
attempt count, timestamps, and an optional safe error code.

Statuses:

| Status | Meaning |
| --- | --- |
| `accepted` | Request accepted by an API boundary |
| `queued` | Waiting for a worker |
| `running` | Claimed by a worker |
| `blocked` | Waiting for an explicit operational resolution |
| `succeeded` | Processing and publication completed |
| `failed` | Processing ended unsuccessfully |

Stages:

```text
queued -> extracting -> normalizing -> chunking -> embedding -> publishing -> complete
```

`accepted` or `queued` does not mean indexed. Successful indexing requires
complete publication. Durable claiming, leases, retries, and transitions are
future ingestion work and are not implemented by these dataclasses.

## API schemas

Implemented in [`app/schemas/contracts.py`](../app/schemas/contracts.py).
All Pydantic models reject unexpected fields with `extra="forbid"`.

### `AuthorizationScopeRequest`

The external representation of an authorization scope. It preserves empty
collections and permissions instead of converting them to an absent scope.

### `RetrieveRequest`

Contains:

- tenant and collection IDs
- nonblank query text
- required, non-null authorization scope
- optional requested collection IDs
- bounded `top_k`
- optional category/language/date filters

The requested collection set must be a subset of the scope's allowed
collection set. The request's collection must also be allowed. The
`validate_top_k(max_top_k)` method applies the configured application limit
from `Settings`; the schema itself applies the safe absolute range `1..100`.

### `RetrieveResponse` and `SourceReference`

Responses include outcome, evidence chunks, sources, request ID,
configuration revision, and degradation reasons. Source references identify
document, version, chunk, and index revision. They do not expose raw
filesystem paths, credentials, or unrestricted URLs.

### `IngestionRequest`

Ingestion accepts an approved document-version ID and expected checksum. It
does not accept an arbitrary public URL. It also requires configuration
revision, idempotency key, and authorization scope.

### Other response schemas

- `IngestionAcceptedResponse`: job ID, status, and request ID.
- `IngestionStatusResponse`: job state, stage, attempt count, and timestamps.
- `ErrorResponse`: safe error code/message, request ID, and retryable flag.
- `ReadinessResponse`: status, named checks, and optional table count. The
  optional `table_count` preserves compatibility with the current `/ready`
  response.

## Examples and fixtures

Non-sensitive, fictional school-training examples are under
[`tests/fixtures/contracts/`](../tests/fixtures/contracts/):

- `valid_retrieval_request.json`
- `explicitly_empty_permissions.json`
- `valid_ingestion_request.json`
- `safe_error.json`

The examples use UUIDs and fictional values only. They do not contain real
school records, credentials, source URLs, or database details.

## Validation coverage

The contract tests verify:

- required/non-null scope
- empty permission scopes as explicit no-access values
- collection subset checks
- tenant/scope matching
- immutable internal collections
- timezone-aware dates
- lifecycle date ordering
- checksum shape
- positive token counts and dimensions
- finite scores and positive ranks
- readiness response compatibility
- safe error response shape

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit\test_contracts_step1.py tests\contract\test_contract_serialization.py -q
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m ruff format --check app tests
.\.venv\Scripts\python.exe -m mypy app tests
```

## Unresolved decisions and assumptions

1. External Java identifiers currently use UUID types because the existing
   repository contracts use UUIDs. If Java sends non-UUID tenant, principal,
   collection, or permission identifiers, the boundary types must be changed
   together and contract tests updated.
2. Approval statuses and job transitions are currently represented as strings
   and enums; the persistence transition policy belongs in the ingestion
   service and database layer.
3. `SourceReference.source_locations` is a schema-level JSON-compatible
   structure until a dedicated public source-location schema is needed.
4. The current contract work does not claim SQL tenant isolation, ACL
   enforcement, migrations, durable ingestion, or working retrieval.
