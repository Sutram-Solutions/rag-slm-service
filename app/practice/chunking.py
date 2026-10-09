from sentence_transformers import SentenceTransformer
import numpy as np

document = """
School Fees
School fees must be paid by 10 June.
Parents can pay through the school portal.

School Timings
Classes begin at 8:30 AM and end at 2:30 PM.
Students should arrive ten minutes before classes begin.

School Uniform
Students must wear the prescribed uniform.
Sports uniform is required on Wednesdays.
"""


def chunk_by_paragraph(text: str) -> list[str]:
    paragraphs = text.strip().split("\n\n")

    chunks = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    return chunks


def main() -> None:
    chunks = chunk_by_paragraph(document)

    print(f"Total chunks: {len(chunks)}")

    print("\nLoading the embedding model...")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    embeddings = model.encode_document(
        chunks,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    print(f"\nEmbedding shape: {embeddings.shape}")

    for number, (chunk, embedding) in enumerate(
        zip(chunks, embeddings),
        start=1,
    ):
        print(f"\n--- Chunk {number} ---")
        print(chunk)
        print(f"Vector dimensions: {len(embedding)}")
        print(f"First five values: {embedding[:5]}")

    question = "what to wear on wednesday?"

    query_embedding = model.encode_query(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    print(f"\nQuestion: {question}")
    print(f"Question vector shape: {query_embedding.shape}")

    # Both query and chunk vectors are normalized.
    # Their dot product therefore gives cosine similarity.
    similarity_scores = embeddings @ query_embedding

    # Highest similarity first.
    ranked_indices = np.argsort(similarity_scores)[::-1]

    print("\n--- Search Results ---")

    for rank, chunk_index in enumerate(ranked_indices, start=1):
        score = float(similarity_scores[chunk_index])

        print(f"\nRank {rank} | Chunk {chunk_index + 1}")
        print(f"Similarity: {score:.4f}")
        print(chunks[chunk_index])


if __name__ == "__main__":
    main()
