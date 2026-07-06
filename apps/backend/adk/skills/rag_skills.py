"""
RAG Agent Skills
================
Explicit retrieval skill functions for the RAG domain.

Three distinct skills expose different retrieval modes:
  - search_textbook     : General textbook chunk retrieval
  - search_notes        : Notes/summary-focused retrieval
  - search_exam_papers  : Exam-paper and past-question retrieval

All three share a common internal _retrieve helper that delegates
to EmbeddingService + VectorStore, matching the existing
curriculum_tool pattern.

Skills are called by:
  - RAGAgent (ADK) for intent-aware retrieval dispatch
  - knowledge_server (MCP) via search_curriculum, get_notes,
    get_previous_questions
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def _retrieve(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: Optional[str] = None,
    chapter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Internal shared retrieval helper.

    Generates a dense embedding for the query, applies metadata
    filters, performs pgvector similarity search, and returns
    formatted chunks with source references.

    Args:
        query:   Search query string.
        subject: Academic subject ('physics' or 'chemistry').
        board:   Education board / university slug.
        year:    Year of study slug.
        exam:    Optional entrance exam filter ('kcet' or 'neet').
        chapter: Optional chapter constraint ('Part-1' or 'Part-2').

    Returns:
        Dict with keys:
          chunks  (list[dict])  - formatted chunk dicts
          sources (list[dict])  - source reference dicts
    """
    from app.services.embedding_service import EmbeddingService
    from app.services.vector_store import VectorStore

    embedder = EmbeddingService()
    vector_store = VectorStore()

    embedding = await embedder.embed_text(query)
    raw_chunks = await vector_store.search_chunks(
        embedding=embedding,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
        chapter=chapter,
    )

    formatted_chunks = [
        {
            "content": c.get("content"),
            "title": c.get("title", "Curriculum Document"),
            "source_title": c.get("title", "Curriculum Document"),
            "chapter": c.get("chapter"),
            "page_number": c.get("page_number"),
        }
        for c in raw_chunks
    ]

    return {
        "chunks": formatted_chunks,
        "sources": formatted_chunks,
    }


async def search_textbook(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: Optional[str] = None,
    chapter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve general textbook curriculum chunks for a query.

    Performs metadata-filtered pgvector similarity search and
    returns the top-k chunks most relevant to the query from
    NCERT / board textbook content.

    Args:
        query:   Student query or topic string.
        subject: Academic subject ('physics' or 'chemistry').
        board:   Education board slug (e.g. 'karnataka_state_board').
        year:    Year of study slug (e.g. '2nd_puc').
        exam:    Optional entrance exam filter.
        chapter: Optional chapter volume constraint.

    Returns:
        Dict with 'chunks' and 'sources' lists.
    """
    logger.info(
        f"rag_skill: search_textbook called, subject={subject}, exam={exam}"
    )
    return await _retrieve(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
        chapter=chapter,
    )


async def search_notes(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve notes-oriented curriculum chunks for summary/quick-notes tasks.

    Uses the same retrieval pipeline as search_textbook but signals
    to callers that the intent is notes generation. The chapter
    constraint is left open to maximise coverage across both
    curriculum volumes.

    Args:
        query:   Topic or chapter for note generation.
        subject: Academic subject.
        board:   Education board slug.
        year:    Year of study slug.
        exam:    Optional entrance exam filter.

    Returns:
        Dict with 'chunks' and 'sources' lists.
    """
    logger.info(
        f"rag_skill: search_notes called, subject={subject}, exam={exam}"
    )
    return await _retrieve(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
        chapter=None,  # No chapter restriction — pull across full curriculum
    )


async def search_exam_papers(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: str,
) -> Dict[str, Any]:
    """
    Retrieve exam-paper and past-question chunks for entrance preparation.

    Applies a mandatory exam filter ('kcet' or 'neet') to restrict
    retrieval to exam-tagged curriculum content. Raises ValueError
    if no exam is specified, preventing unfiltered full-corpus scans.

    Args:
        query:   Topic or concept for exam-focused retrieval.
        subject: Academic subject.
        board:   Education board slug.
        year:    Year of study slug.
        exam:    Mandatory entrance exam filter ('kcet' or 'neet').

    Returns:
        Dict with 'chunks' and 'sources' lists.

    Raises:
        ValueError: If exam is not provided or is 'none'.
    """
    if not exam or exam.lower() == "none":
        raise ValueError(
            "search_exam_papers requires a valid exam filter ('kcet' or 'neet'). "
            "Use search_textbook for general retrieval."
        )

    logger.info(
        f"rag_skill: search_exam_papers called, subject={subject}, exam={exam}"
    )
    return await _retrieve(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam.lower(),
        chapter=None,
    )
