# ADR 0003: Embedding storage

Embedding model revision, tokenizer revision, dimensions, preprocessing,
normalization, and distance metric are part of an index revision. Incompatible
vectors must never be mixed. Physical vector storage will be selected when
the first real adapter is implemented; this scaffold does not create a
misleading arbitrary-dimension column.
