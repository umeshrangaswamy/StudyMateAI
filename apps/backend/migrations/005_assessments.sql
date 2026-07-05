-- Create student_assessments table to track quiz attempts and subjective feedback
CREATE TABLE IF NOT EXISTS student_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(100),
    subject VARCHAR(50) NOT NULL,
    exam VARCHAR(50),
    score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fast lookup indexes by subject area and entrance exam scope
CREATE INDEX IF NOT EXISTS idx_assessments_subject ON student_assessments(subject);
CREATE INDEX IF NOT EXISTS idx_assessments_exam ON student_assessments(exam);
