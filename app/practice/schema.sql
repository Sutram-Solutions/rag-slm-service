CREATE TABLE rag.practice_chunks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    embedding_model TEXT NOT NULL
);


SELECT current_user;
