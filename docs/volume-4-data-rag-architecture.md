# Volume 4 – Data Architecture & RAG Design
## StudyMateAI– Enterprise Data & Knowledge Architecture (Version 1.0)

## 1. Purpose
This document defines the data and RAG architecture for StudyMateAI.

Goals:
- Store trusted academic content
- Support metadata-driven retrieval
- Reduce hallucination
- Ground answers in curriculum data
- Support KCET and NEET preparation
- Use the same vector database architecture from MVP to production

## 2. Core Principles
1. Curriculum-first grounding
2. Metadata filtering before vector search
3. Explainable source references
4. PostgreSQL + pgvector from Day 1
5. No vector database migration later
6. Separate knowledge data from user/session data

## 3. MVP Data Stack
```text
Cloud Storage
  -> Ingestion Pipeline
  -> Chunking
  -> Vertex AI Embeddings
  -> Cloud SQL PostgreSQL + pgvector
  -> RAG Agent
  -> SME Agent
```

## 4. Enterprise Data Stack
```text
Cloud Storage
  -> Document Processing Pipeline
  -> Metadata Extraction
  -> Chunking Engine
  -> Embedding Service
  -> Cloud SQL HA + pgvector
  -> RAG Agent
  -> Evaluation Layer
  -> SME + Personalization Agents
  -> Analytics
```

## 5. Knowledge Sources
### MVP
Physics:
- Textbooks
- Notes
- NEET material
- KCET question banks

Chemistry:
- Textbooks
- Notes
- NEET material
- KCET question banks

### Enterprise
Additional:
- Mathematics
- Biology
- English
- University notes
- Lab manuals
- Previous papers
- Teacher notes

## 6. Document Storage
### MVP Bucket Structure
```text
knowledge/
  physics/
    textbooks/
    notes/
    kcet/
    neet/
  chemistry/
    textbooks/
    notes/
    kcet/
    neet/
```

### Enterprise Bucket Structure
```text
knowledge/
  physics/
  chemistry/
  mathematics/
  biology/
  english/
  university/
  entrance-exams/
  reference-material/
```

## 7. Required Metadata
Every document and chunk must carry metadata.

```json
{
  "subject": "physics",
  "board": "karnataka_state_board",
  "year": "2nd_puc",
  "chapter": "ray_optics",
  "topic": "refraction",
  "content_type": "textbook",
  "exam": "neet",
  "source": "internal_notes"
}
```

## 8. PostgreSQL Extensions
Required extensions:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

## 9. Core Tables
### documents
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  board TEXT NOT NULL,
  year TEXT NOT NULL,
  chapter TEXT,
  document_type TEXT,
  source TEXT,
  gcs_path TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

### curriculum_chunks
```sql
CREATE TABLE curriculum_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES documents(id),
  subject TEXT NOT NULL,
  board TEXT NOT NULL,
  year TEXT NOT NULL,
  chapter TEXT,
  topic TEXT,
  exam TEXT,
  content TEXT NOT NULL,
  page_number INTEGER,
  created_at TIMESTAMP DEFAULT now()
);
```

### chunk_embeddings
```sql
CREATE TABLE chunk_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chunk_id UUID REFERENCES curriculum_chunks(id),
  embedding vector(768),
  created_at TIMESTAMP DEFAULT now()
);
```

Note: embedding dimension must match the selected embedding model output dimension.

### student_assessments
```sql
CREATE TABLE student_assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id TEXT,
  subject TEXT,
  exam TEXT,
  score NUMERIC,
  feedback TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

## 10. Indexing Strategy
Indexes:
- subject
- board
- year
- chapter
- exam
- vector similarity index when enough data is available

## 11. Chunking Strategy
MVP:
- 250–350 tokens
- target: 300 tokens
- overlap: 10%

Enterprise:
- adaptive chunking by content type
- formula-aware chunking
- question-aware chunking
- page and diagram references

## 12. Embedding Strategy
Model:
- text-embedding-004 or configured Vertex AI embedding model

Only embed:
- academic content
- notes
- question banks
- syllabi

Do not embed:
- secrets
- logs
- user PII
- credentials

## 13. Retrieval Pipeline
```text
Student query
  -> Detect metadata
  -> Generate query embedding
  -> Metadata filter
  -> pgvector similarity search
  -> Top 3 chunks
  -> Context compression
  -> SME Agent
  -> Response with sources
```

## 14. Metadata Filtering Rule
Before vector search, always filter by:
- subject
- board
- year
- optional exam
- optional chapter/topic when detected

Example:
```sql
SELECT c.content, c.chapter, c.topic, c.page_number,
       e.embedding <=> :query_embedding AS distance
FROM curriculum_chunks c
JOIN chunk_embeddings e ON e.chunk_id = c.id
WHERE c.subject = :subject
  AND c.board = :board
  AND c.year = :year
ORDER BY distance
LIMIT 3;
```

## 15. Grounding Strategy
SME agents should receive RAG context before generating academic responses.

Preferred mode:
```text
RAG + SME
```

Avoid:
```text
SME-only unsupported generation
```

## 16. Entrance Exam Data Design
### NEET
Store:
- syllabus
- important questions
- previous papers
- topic weightage
- revision notes

### KCET
Store:
- previous papers
- question trends
- chapter importance
- formulas
- revision notes

## 17. Evaluator Data
MVP:
- Store recent assessment results only

Enterprise:
- Store historical performance
- Track weak topics
- Build adaptive learning profile

## 18. Data Lifecycle
### MVP
- Knowledge content: permanent
- Query logs: 30 days
- Assessment results: 90 days

### Enterprise
- archival policies
- retention schedules
- compliance deletion
- analytics export

## 19. Locked Data Decisions
- Use Cloud Storage for documents.
- Use Cloud SQL PostgreSQL + pgvector for RAG.
- Use Firestore only for lightweight metadata/session data.
- Do not use ChromaDB, Pinecone, or Vertex AI Vector Search in MVP.
- Always use metadata filtering before vector similarity search.
