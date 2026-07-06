"""
Chemistry Agent Skills
======================
Explicit skill functions for the Chemistry SME domain.

Each skill maps to a well-defined pedagogical capability and sets
the correct `intent` string before delegating to ChemistrySMEAgent.
Skills are called by:
  - ChemistryAgent (ADK) for direct dispatch
  - knowledge_server (MCP) via get_formula_sheet (equation sheet variant)
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def explain_concept(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
) -> str:
    """
    Explain a Chemistry concept clearly and concisely in a teacher-like manner.

    Generates a structured explanation with:
      - Short heading
      - Concept definition
      - Explanation with chemical example / equation
      - Exam tip when KCET/NEET is detected

    Args:
        query:   The student's question or concept to explain.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus ('kcet' or 'neet').

    Returns:
        Formatted explanation text string.
    """
    logger.info(f"chemistry_skill: explain_concept called, exam={exam}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="lesson_explanation",
        exam=exam,
        context=context,
    )


async def generate_summary(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
) -> str:
    """
    Generate a 5–10 bullet-point lesson summary grounded in curriculum content.

    Suitable for quick revision before board exams, KCET, or NEET.

    Args:
        query:   Topic or chapter to summarize.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus.

    Returns:
        Bullet-point summary text string.
    """
    logger.info(f"chemistry_skill: generate_summary called, exam={exam}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="lesson_summary",
        exam=exam,
        context=context,
    )


async def generate_quick_notes(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
) -> str:
    """
    Generate 10–15 concise bullet-point study notes for rapid revision.

    Notes include key reactions, reagents, conditions, exceptions,
    and exam-relevant facts.

    Args:
        query:   Topic or chapter for notes generation.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus.

    Returns:
        Quick notes text string.
    """
    logger.info(f"chemistry_skill: generate_quick_notes called, exam={exam}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="quick_notes",
        exam=exam,
        context=context,
    )


async def prepare_kcet(
    query: str,
    context: List[Dict[str, Any]],
) -> str:
    """
    Generate a KCET-focused Chemistry preparation response.

    Emphasises Karnataka CET exam patterns, weightage, and
    frequently tested reactions/concepts for the given topic.

    Args:
        query:   Topic or chapter for KCET preparation.
        context: RAG-retrieved curriculum chunks.

    Returns:
        KCET-aligned preparation text string.
    """
    logger.info("chemistry_skill: prepare_kcet called")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="entrance_preparation",
        exam="kcet",
        context=context,
    )


async def prepare_neet(
    query: str,
    context: List[Dict[str, Any]],
) -> str:
    """
    Generate a NEET-focused Chemistry preparation response.

    Emphasises NEET exam patterns, NTA weightage, and
    frequently tested reactions/concepts for the given topic.

    Args:
        query:   Topic or chapter for NEET preparation.
        context: RAG-retrieved curriculum chunks.

    Returns:
        NEET-aligned preparation text string.
    """
    logger.info("chemistry_skill: prepare_neet called")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="entrance_preparation",
        exam="neet",
        context=context,
    )


async def generate_equation_sheet(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
) -> str:
    """
    Generate a compact chemical equation sheet for a Chemistry topic.

    Lists key reactions, balanced equations, reaction conditions,
    reagents, and products. Includes IUPAC naming where relevant.
    Suitable for last-minute revision before KCET/NEET/Board exams.

    Args:
        query:   Topic or chapter for equation extraction.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus.

    Returns:
        Formatted equation sheet text string.
    """
    logger.info(f"chemistry_skill: generate_equation_sheet called, exam={exam}")
    equation_query = f"List all important chemical equations and reactions for: {query}"
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=equation_query,
        intent="quick_notes",
        exam=exam,
        context=context,
    )
