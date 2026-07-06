# Architecture Decision Record (ADR) - 001: RAG Grounding Strategy

## Status
Approved

## Context
StudyMateAI requires grounding its responses in the official curriculum (NCERT textbooks) to maintain strict syllabus compliance, prevent hallucinations, and guarantee academic accuracy.

## Decision
We implement a dense-retrieval RAG pipeline utilizing PostgreSQL with the `pgvector` extension:
- **Embedding Generation**: All curriculum documents are chunked (250–350 tokens) and embedded using Vertex AI `text-embedding-004` (768 dimensions).
- **Storage**: Vectors and metadata are stored in a Cloud SQL PostgreSQL instance.
- **Search Pre-filtering**: Before computing vector similarity, the query is pre-filtered by subject, board, year of study, and chapter in SQL to optimize performance and security.
- **Top-K Limit**: The pipeline retrieves exactly `top_k = 3` context chunks per query to minimize LLM context token consumption and control costs.

## Consequences
- **Pros**: Guaranteed factual alignment, zero hallucination on non-existent topics, and predictable token costs.
- **Cons**: Requires keeping pgvector indices synchronized with textbook changes.
