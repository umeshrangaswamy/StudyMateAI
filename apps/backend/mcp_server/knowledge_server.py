"""
Knowledge MCP Server
====================
Exposes curriculum search, notes, formula sheets, and past questions as MCP tools.
"""

import logging
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("Knowledge Server")


@mcp.tool()
async def search_curriculum(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: Optional[str] = None,
    chapter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve general textbook curriculum chunks for a query.

    Args:
        query:   Search query string.
        subject: Academic subject ('physics' or 'chemistry').
        board:   Education board slug (e.g. 'karnataka_state_board').
        year:    Year of study slug (e.g. '2nd_puc').
        exam:    Optional entrance exam filter ('kcet' or 'neet').
        chapter: Optional chapter volume constraint ('Part-1' or 'Part-2').
    """
    logger.info(f"MCP tool search_curriculum called: subject={subject}, exam={exam}")
    from adk.skills.rag_skills import search_textbook
    return await search_textbook(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
        chapter=chapter,
    )


@mcp.tool()
async def get_notes(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve notes-oriented curriculum chunks for summary or quick-notes tasks.

    Args:
        query:   Topic or chapter for note generation.
        subject: Academic subject.
        board:   Education board slug.
        year:    Year of study slug.
        exam:    Optional entrance exam filter.
    """
    logger.info(f"MCP tool get_notes called: subject={subject}, exam={exam}")
    from adk.skills.rag_skills import search_notes
    return await search_notes(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
    )


@mcp.tool()
async def get_formula_sheet(
    query: str,
    subject: str,
    exam: Optional[str] = None,
    context_chunks: Optional[list] = None,
) -> str:
    """
    Generate a formula or equation sheet for a given topic.

    Args:
        query:          Topic or chapter name.
        subject:        Academic subject ('physics' or 'chemistry').
        exam:           Optional entrance exam focus ('kcet' or 'neet').
        context_chunks: Optional list of retrieved chunks. If empty, a search will be performed.
    """
    logger.info(f"MCP tool get_formula_sheet called: subject={subject}")
    # Resolve chunks if not provided
    chunks = context_chunks
    if not chunks:
        from adk.skills.rag_skills import search_notes
        retrieved = await search_notes(
            query=query,
            subject=subject,
            board="karnataka_state_board",  # fallback defaults for retrieval
            year="2nd_puc",
            exam=exam,
        )
        chunks = retrieved.get("chunks", [])

    if subject.lower() == "physics":
        from adk.skills.physics_skills import generate_formula_sheet
        return await generate_formula_sheet(query=query, context=chunks, exam=exam)
    else:
        from adk.skills.chemistry_skills import generate_equation_sheet
        return await generate_equation_sheet(query=query, context=chunks, exam=exam)


@mcp.tool()
async def get_previous_questions(
    query: str,
    subject: str,
    board: str,
    year: str,
    exam: str,
) -> Dict[str, Any]:
    """
    Retrieve exam paper chunks containing previous questions.

    Args:
        query:   Topic or concept.
        subject: Academic subject.
        board:   Education board slug.
        year:    Year of study slug.
        exam:    Mandatory entrance exam filter ('kcet' or 'neet').
    """
    logger.info(f"MCP tool get_previous_questions called: exam={exam}")
    from adk.skills.rag_skills import search_exam_papers
    return await search_exam_papers(
        query=query,
        subject=subject,
        board=board,
        year=year,
        exam=exam,
    )
