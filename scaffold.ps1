#requires -Version 5.1
<#
Creates the RAG framework folder and file skeleton.
Idempotent: existing folders and files are left completely untouched.
All created .py files are zero bytes.
#>

$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

$created = 0
$skipped = 0
$dirsMade = 0

function New-Skeleton {
    param([string]$Relative)

    $full = Join-Path $script:root $Relative
    $dir  = Split-Path $full -Parent

    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        $script:dirsMade++
    }

    if (Test-Path -LiteralPath $full) {
        $script:skipped++
        return
    }

    # Zero-byte file. No content, no BOM.
    [System.IO.File]::WriteAllBytes($full, @())
    $script:created++
}

$files = @(
  'app/__init__.py','app/main.py',

  'app/api/__init__.py',
  'app/api/routes/__init__.py','app/api/routes/retrieval.py',
  'app/api/routes/ingestion.py','app/api/routes/health.py',
  'app/api/middleware/__init__.py','app/api/middleware/request_context.py',
  'app/api/middleware/request_limits.py','app/api/middleware/rate_limit.py',
  'app/api/exception_handlers.py',

  'app/schemas/__init__.py','app/schemas/common.py','app/schemas/retrieval.py',
  'app/schemas/preview.py','app/schemas/ingestion.py','app/schemas/collections.py',
  'app/schemas/jobs.py','app/schemas/errors.py','app/schemas/health.py',
  'app/schemas/validators.py',

  'app/domain/__init__.py','app/domain/documents.py','app/domain/extraction.py',
  'app/domain/chunks.py','app/domain/embeddings.py','app/domain/retrieval.py',
  'app/domain/security.py','app/domain/jobs.py','app/domain/evaluation.py',
  'app/domain/budget.py','app/domain/context.py',

  'app/core/__init__.py','app/core/config.py','app/core/lifecycle.py',
  'app/core/dependencies.py','app/core/collection_config.py','app/core/deadlines.py',
  'app/core/fingerprint.py','app/core/startup.py','app/core/exceptions.py',
  'app/core/constants.py',

  'app/security/__init__.py','app/security/service_auth.py',
  'app/security/authorization.py','app/security/sql_scope.py','app/security/files.py',
  'app/security/redaction.py','app/security/audit.py','app/security/content_risk.py',
  'app/security/policy.py',

  'app/storage/__init__.py','app/storage/ports.py','app/storage/local.py',
  'app/storage/object_store.py','app/storage/integrity.py',

  'app/adapters/__init__.py','app/adapters/http.py','app/adapters/school_content.py',
  'app/adapters/servly_content.py','app/adapters/coaching_content.py',

  'app/normalization/__init__.py','app/normalization/policy.py',
  'app/normalization/steps.py',

  'app/ingestion/__init__.py','app/ingestion/service.py','app/ingestion/pipeline.py',
  'app/ingestion/worker.py','app/ingestion/jobs.py','app/ingestion/idempotency.py',
  'app/ingestion/checkpoints.py','app/ingestion/validation.py','app/ingestion/quality.py',
  'app/ingestion/publication.py','app/ingestion/reprocessing.py','app/ingestion/replay.py',
  'app/ingestion/freshness.py','app/ingestion/deletion.py','app/ingestion/cleanup.py',
  'app/ingestion/writer.py',

  'app/ingestion/extractors/__init__.py','app/ingestion/extractors/base.py',
  'app/ingestion/extractors/registry.py','app/ingestion/extractors/text.py',
  'app/ingestion/extractors/pdf.py','app/ingestion/extractors/docx.py',
  'app/ingestion/extractors/html.py','app/ingestion/extractors/xlsx.py',
  'app/ingestion/extractors/tables.py','app/ingestion/extractors/layout.py',
  'app/ingestion/extractors/structure.py',
  'app/ingestion/extractors/ocr/__init__.py','app/ingestion/extractors/ocr/base.py',
  'app/ingestion/extractors/ocr/tesseract.py','app/ingestion/extractors/ocr/quality.py',

  'app/ingestion/cleaning/__init__.py','app/ingestion/cleaning/pipeline.py',
  'app/ingestion/cleaning/artifacts.py','app/ingestion/cleaning/boilerplate.py',
  'app/ingestion/cleaning/dedupe.py','app/ingestion/cleaning/encoding.py',
  'app/ingestion/cleaning/guards.py',

  'app/ingestion/chunking/__init__.py','app/ingestion/chunking/base.py',
  'app/ingestion/chunking/fixed.py','app/ingestion/chunking/structure.py',
  'app/ingestion/chunking/document_unit.py','app/ingestion/chunking/semantic.py',
  'app/ingestion/chunking/oversize.py','app/ingestion/chunking/overlap.py',
  'app/ingestion/chunking/tables.py','app/ingestion/chunking/identity.py',
  'app/ingestion/chunking/validation.py',

  'app/nlp/__init__.py','app/nlp/language.py','app/nlp/sentences.py',
  'app/nlp/transliteration.py','app/nlp/numbers.py','app/nlp/entities.py',
  'app/nlp/dates.py','app/nlp/pii.py','app/nlp/metadata.py',

  'app/tokenization/__init__.py','app/tokenization/base.py',
  'app/tokenization/adapters.py','app/tokenization/heuristic.py',
  'app/tokenization/budget.py','app/tokenization/inflation.py',

  'app/embeddings/__init__.py','app/embeddings/base.py','app/embeddings/local.py',
  'app/embeddings/remote.py','app/embeddings/service.py','app/embeddings/batching.py',
  'app/embeddings/validation.py','app/embeddings/normalize.py',
  'app/embeddings/compatibility.py','app/embeddings/registry.py',
  'app/embeddings/truncation.py','app/embeddings/execution.py',
  'app/embeddings/cache.py','app/embeddings/migration.py',

  'app/db/__init__.py','app/db/base.py','app/db/session.py','app/db/transactions.py',
  'app/db/models/__init__.py','app/db/models/tenant.py','app/db/models/collection.py',
  'app/db/models/document.py','app/db/models/chunk.py','app/db/models/embedding.py',
  'app/db/models/job.py','app/db/models/idempotency.py','app/db/models/audit.py',
  'app/db/models/retrieval_event.py','app/db/models/feedback.py',
  'app/db/models/usage.py','app/db/models/evaluation_run.py',
  'app/db/repositories/__init__.py','app/db/repositories/base.py',
  'app/db/repositories/documents.py','app/db/repositories/collections.py',
  'app/db/repositories/chunks.py','app/db/repositories/jobs.py',
  'app/db/repositories/audit.py',
  'app/db/search/__init__.py','app/db/search/vector.py','app/db/search/keyword.py',
  'app/db/search/trigram.py',
  'app/db/mappers/__init__.py','app/db/mappers/chunk.py','app/db/mappers/document.py',

  'app/retrieval/__init__.py','app/retrieval/service.py','app/retrieval/query.py',
  'app/retrieval/filters.py','app/retrieval/vector.py','app/retrieval/keyword.py',
  'app/retrieval/trigram.py','app/retrieval/hybrid.py','app/retrieval/fusion.py',
  'app/retrieval/deduplication.py','app/retrieval/selection.py',
  'app/retrieval/relevance.py','app/retrieval/lifecycle.py','app/retrieval/conflicts.py',
  'app/retrieval/sources.py','app/retrieval/results.py','app/retrieval/empty.py',
  'app/retrieval/expansion.py','app/retrieval/shadow.py',
  'app/retrieval/reranking/__init__.py','app/retrieval/reranking/base.py',
  'app/retrieval/reranking/local.py','app/retrieval/reranking/fallback.py',
  'app/retrieval/reranking/threadpool.py',

  'app/context/__init__.py','app/context/assembler.py','app/context/citations.py',
  'app/context/budget.py','app/context/policy.py','app/context/provenance.py',

  'app/observability/__init__.py','app/observability/logging.py',
  'app/observability/context.py','app/observability/redaction.py',
  'app/observability/metrics.py','app/observability/tracing.py',
  'app/observability/events.py','app/observability/feedback.py',
  'app/observability/usage.py','app/observability/health.py',
  'app/observability/audit.py',

  'app/resilience/__init__.py','app/resilience/retry.py','app/resilience/timeouts.py',
  'app/resilience/concurrency.py','app/resilience/backpressure.py',
  'app/resilience/degradation.py','app/resilience/circuit_breaker.py',

  'app/cache/__init__.py','app/cache/base.py','app/cache/keys.py',
  'app/cache/invalidation.py',

  'app/operations/__init__.py','app/operations/shutdown.py',

  'app/admin/__init__.py','app/admin/reindex.py','app/admin/diagnostics.py',
  'app/admin/cli.py',

  'app/common/__init__.py','app/common/hashing.py','app/common/time.py',
  'app/common/identifiers.py','app/common/serialization.py','app/common/batching.py',
  'app/common/async_utils.py','app/common/text.py','app/common/files.py',

  'evaluation/__init__.py',
  'evaluation/datasets/__init__.py','evaluation/datasets/loader.py',
  'evaluation/datasets/validation.py','evaluation/datasets/statistics.py',
  'evaluation/datasets/snapshots.py','evaluation/datasets/labelling.py',
  'evaluation/runners/__init__.py','evaluation/runners/retrieval.py',
  'evaluation/metrics/__init__.py','evaluation/metrics/retrieval.py',
  'evaluation/metrics/answerability.py','evaluation/metrics/performance.py',
  'evaluation/experiments/__init__.py','evaluation/experiments/runner.py',
  'evaluation/experiments/comparison.py','evaluation/experiments/statistics.py',
  'evaluation/coverage.py',
  'evaluation/reports/__init__.py','evaluation/reports/writer.py',
  'evaluation/gates.py','evaluation/feedback.py','evaluation/answers.py',

  'tests/__init__.py','tests/conftest.py',
  'tests/fakes/__init__.py','tests/fakes/embeddings.py','tests/fakes/storage.py',
  'tests/fakes/reranking.py','tests/fakes/auth.py','tests/fakes/clock.py',
  'tests/builders/__init__.py','tests/builders/chunk_builder.py',
  'tests/builders/document_builder.py','tests/builders/acl_builder.py',
  'tests/unit/__init__.py','tests/integration/__init__.py','tests/security/__init__.py',
  'tests/contract/__init__.py','tests/resilience/__init__.py','tests/e2e/__init__.py',
  'tests/migrations/__init__.py','tests/fixtures/.gitkeep',

  'migrations/.gitkeep','migrations/versions/.gitkeep',
  'infra/.gitkeep','docs/adr/.gitkeep','docs/runbooks/.gitkeep'
)

Write-Host "Scaffolding into $root" -ForegroundColor Cyan
Write-Host ""

foreach ($f in $files) { New-Skeleton -Relative $f }

Write-Host "Directories created : $dirsMade"
Write-Host "Files created       : $created" -ForegroundColor Green
Write-Host "Files skipped       : $skipped" -ForegroundColor Yellow
Write-Host "Total declared      : $($files.Count)"
Write-Host ""
Write-Host "Existing files were not modified." -ForegroundColor Cyan
