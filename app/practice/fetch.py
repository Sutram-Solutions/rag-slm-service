from getpass import getpass

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    question = input("Your question: ").strip()
    if not question:
        print("Please enter a question.")
        return

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode_query(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    username = "postgres"
    password = "dev"

    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="platform",
        user=username,
        password=password,
        connect_timeout=10,
    ) as connection:
        register_vector(connection)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    chunk_index,
                    content,
                    1 - (embedding <=> %s) AS similarity
                FROM rag.practice_chunks
                WHERE embedding_model = %s
                ORDER BY embedding <=> %s
                LIMIT 3
                """,
                (
                    Vector(query_embedding),
                    MODEL_NAME,
                    Vector(query_embedding),
                ),
            )
            results = cursor.fetchall()

    print("\n--- PostgreSQL Search Results ---")

    for rank, (chunk_index, content, similarity) in enumerate(results, start=1):
        print(f"\nRank {rank} | Chunk {chunk_index}")
        print(f"Similarity: {similarity:.4f}")
        print(content)


if __name__ == "__main__":
    main()
