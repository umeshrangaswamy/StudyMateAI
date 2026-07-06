"""
Physics Agent Skills
====================
Explicit skill functions for the Physics SME domain.

Each skill maps to a well-defined pedagogical capability and sets
the correct `intent` string before delegating to PhysicsSMEAgent.
Skills are called by:
  - PhysicsAgent (ADK) for direct dispatch
  - knowledge_server (MCP) via get_formula_sheet
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
    Explain a Physics concept clearly and concisely in a teacher-like manner.

    Generates a structured explanation with:
      - Short heading
      - Simple explanation grounded in curriculum
      - Real-life example
      - Formula if applicable
      - KCET/NEET tip when exam is detected

    Args:
        query:   The student's question or concept to explain.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus ('kcet' or 'neet').

    Returns:
        Formatted explanation text string.
    """
    logger.info(f"physics_skill: explain_concept called, exam={exam}")
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
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
    logger.info(f"physics_skill: generate_summary called, exam={exam}")
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
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

    Notes are denser than a summary and include key terms, units,
    and exam-relevant facts.

    Args:
        query:   Topic or chapter for notes generation.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus.

    Returns:
        Quick notes text string.
    """
    logger.info(f"physics_skill: generate_quick_notes called, exam={exam}")
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
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
    Generate a KCET-focused Physics preparation response.

    Emphasises Karnataka CET exam patterns, weightage, and
    frequently tested concepts for the given topic.

    Args:
        query:   Topic or chapter for KCET preparation.
        context: RAG-retrieved curriculum chunks.

    Returns:
        KCET-aligned preparation text string.
    """
    logger.info("physics_skill: prepare_kcet called")
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
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
    Generate a NEET-focused Physics preparation response.

    Emphasises NEET exam patterns, NTA weightage, and
    frequently tested concepts for the given topic.

    Args:
        query:   Topic or chapter for NEET preparation.
        context: RAG-retrieved curriculum chunks.

    Returns:
        NEET-aligned preparation text string.
    """
    logger.info("physics_skill: prepare_neet called")
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="entrance_preparation",
        exam="neet",
        context=context,
    )


async def generate_formula_sheet(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
) -> str:
    """
    Generate a compact formula sheet for a Physics topic.

    Lists all relevant formulae with symbol definitions,
    SI units, and a brief applicability note. Suitable for
    last-minute revision before KCET/NEET/Board exams.

    Args:
        query:   Topic or chapter for formula extraction.
        context: RAG-retrieved curriculum chunks.
        exam:    Optional entrance exam focus.

    Returns:
        Formatted formula sheet text string.
    """
    logger.info(f"physics_skill: generate_formula_sheet called, exam={exam}")
    formula_query = f"List all important formulae for: {query}"
    from app.agents.physics_sme import PhysicsSMEAgent
    sme = PhysicsSMEAgent()
    return await sme.generate_response(
        prompt=formula_query,
        intent="quick_notes",
        exam=exam,
        context=context,
    )
