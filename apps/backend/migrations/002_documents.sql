-- Create documents table to store curriculum textbook references
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    board VARCHAR(100) NOT NULL,
    year VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Metadata indexes for fast lookup filtering
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_documents_board ON documents(board);
CREATE INDEX IF NOT EXISTS idx_documents_year ON documents(year);
