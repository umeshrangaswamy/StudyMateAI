-- Create curriculum_chunks table to store grounded textbook sections
CREATE TABLE IF NOT EXISTS curriculum_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chapter VARCHAR(150),
    page_number INTEGER,
    exam VARCHAR(50), -- e.g. neet, kcet, or null
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fast indexes for chapter search and exam filter combinations
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON curriculum_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chapter ON curriculum_chunks(chapter);
CREATE INDEX IF NOT EXISTS idx_chunks_exam ON curriculum_chunks(exam);
