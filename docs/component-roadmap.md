# Component roadmap

This creation-only scaffold does not claim a complete RAG system.

## Deferred

- Extraction beyond restricted UTF-8 local text.
- OCR, chunking, embeddings, vector search, fusion, and reranking.
- Durable worker execution and lease recovery.
- Java workload identity integration.
- PostgreSQL integration tests requiring disposable pgvector.

Each deferred component must preserve the Java/Python boundary, explicit
authorization scope, pinned embedding revisions, and tenant-qualified SQL.
