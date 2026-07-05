-- CONFIGURATION CONSTRAINT: The vector dimension (768) must match the output shape of Google's text-embedding-004 model.
-- If the embedding model is updated in settings, this column dimension size must be adjusted.
CREATE TABLE IF NOT EXISTS chunk_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES curriculum_chunks(id) ON DELETE CASCADE,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index referencing the parent chunk record
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON chunk_embeddings(chunk_id);

-- HNSW Vector Index mapping for fast cosine similarity RAG searches
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw ON chunk_embeddings USING hnsw (embedding vector_cosine_ops);
