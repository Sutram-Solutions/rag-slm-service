from getpass import getpass
import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
from app.practice.chunking import chunk_by_paragraph, document

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    # Reuse the document and chunking function from your earlier exercise.
    chunks = chunk_by_paragraph(document)

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode_document(
        chunks,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    with psycopg.connect(
        host="localhost",
        port=5433,
        dbname="platform",
        user="postgres",
        password="dev",
        connect_timeout=10,
    ) as connection:
        register_vector(connection)

        with connection.cursor() as cursor:
            # Avoid inserting duplicates if you run this exercise again.
            cursor.execute("SELECT COUNT(*) FROM rag.practice_chunks")
            existing = cursor.fetchone()

            if existing is not None and existing[0] > 0:
                print("Practice table already contains data. Skipping insertion.")
                return

            for chunk_index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings, strict=True),
                start=1,
            ):
                cursor.execute(
                    """
                    INSERT INTO rag.practice_chunks (
                        chunk_index,
                        content,
                        embedding,
                        embedding_model
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        chunk_index,
                        chunk,
                        Vector(embedding),
                        MODEL_NAME,
                    ),
                )

    # Leaving the connection block successfully commits the inserts.
    print(f"Saved {len(chunks)} chunks to PostgreSQL.")


if __name__ == "__main__":
    main()
