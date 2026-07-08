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
    response_style: Optional[str] = "concise",
) -> str:
    """
    Explain a Chemistry concept clearly and concisely in a teacher-like manner.
    """
    logger.info(f"chemistry_skill: explain_concept called, exam={exam}, response_style={response_style}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="lesson_explanation",
        exam=exam,
        context=context,
        response_style=response_style,
    )


async def generate_summary(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
    response_style: Optional[str] = "concise",
) -> str:
    """
    Generate a lesson summary grounded in curriculum content.
    """
    logger.info(f"chemistry_skill: generate_summary called, exam={exam}, response_style={response_style}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="lesson_summary",
        exam=exam,
        context=context,
        response_style=response_style,
    )


async def generate_quick_notes(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
    response_style: Optional[str] = "concise",
) -> str:
    """
    Generate study notes for rapid revision.
    """
    logger.info(f"chemistry_skill: generate_quick_notes called, exam={exam}, response_style={response_style}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="quick_notes",
        exam=exam,
        context=context,
        response_style=response_style,
    )


async def prepare_kcet(
    query: str,
    context: List[Dict[str, Any]],
    response_style: Optional[str] = "concise",
) -> str:
    """
    Generate a KCET-focused Chemistry preparation response.
    """
    logger.info(f"chemistry_skill: prepare_kcet called, response_style={response_style}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="entrance_preparation",
        exam="kcet",
        context=context,
        response_style=response_style,
    )


async def prepare_neet(
    query: str,
    context: List[Dict[str, Any]],
    response_style: Optional[str] = "concise",
) -> str:
    """
    Generate a NEET-focused Chemistry preparation response.
    """
    logger.info(f"chemistry_skill: prepare_neet called, response_style={response_style}")
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=query,
        intent="entrance_preparation",
        exam="neet",
        context=context,
        response_style=response_style,
    )


async def generate_equation_sheet(
    query: str,
    context: List[Dict[str, Any]],
    exam: Optional[str] = None,
    response_style: Optional[str] = "concise",
) -> str:
    """
    Generate a compact chemical equation sheet for a Chemistry topic.
    """
    logger.info(f"chemistry_skill: generate_equation_sheet called, exam={exam}, response_style={response_style}")
    equation_query = f"List all important chemical equations and reactions for: {query}"
    from app.agents.chemistry_sme import ChemistrySMEAgent
    sme = ChemistrySMEAgent()
    return await sme.generate_response(
        prompt=equation_query,
        intent="quick_notes",
        exam=exam,
        context=context,
        response_style=response_style,
    )
