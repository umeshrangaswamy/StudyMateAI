"""
Assessment MCP Server
=====================
Exposes quiz generation, answer evaluation, and revision recommendation as MCP tools.
"""

import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("Assessment Server")


@mcp.tool()
async def generate_quiz(
    year: str,
    board: str,
    subject: str,
    query: str,
    exam: Optional[str] = None,
    chunks: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate exactly 5 multiple-choice questions complete with 4 options, the correct answer, and an explanation.

    Args:
        year:    Year of study.
        board:   Education board slug.
        subject: Academic subject ('physics' or 'chemistry').
        query:   Topic or chapter name.
        exam:    Optional entrance exam focus ('kcet' or 'neet').
        chunks:  Optional list of grounding context chunks.
    """
    logger.info(f"MCP tool generate_quiz called: subject={subject}, exam={exam}")
    from adk.quiz_tool import generate_mcq_quiz
    return await generate_mcq_quiz(
        year=year,
        board=board,
        subject=subject,
        query=query,
        exam=exam,
        chunks=chunks,
    )


@mcp.tool()
async def evaluate_answer(
    questions: List[Dict[str, Any]],
    student_answers: Dict[str, str],
    subject: str,
    exam: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Grade student MCQ or subjective/conceptual reasoning answers.

    Args:
        questions:       List of question dicts.
        student_answers: Student's answers mapped by question ID.
        subject:         Academic subject.
        exam:            Optional entrance exam focus.
    """
    logger.info(f"MCP tool evaluate_answer called: subject={subject}")
    from adk.skills.evaluator_skills import evaluate_answer as eval_skill
    return await eval_skill(
        questions=questions,
        student_answers=student_answers,
        subject=subject,
        exam=exam,
    )


@mcp.tool()
async def recommend_revision(
    evaluation_result: Dict[str, Any],
    subject: str,
) -> Dict[str, Any]:
    """
    Analyze student quiz results to detect weak topics and suggest next revision steps.

    Args:
        evaluation_result: Score, missing points, and tips from evaluate_answer.
        subject:           Academic subject.
    """
    logger.info(f"MCP tool recommend_revision called: subject={subject}")
    from adk.skills.evaluator_skills import detect_weak_topics
    return await detect_weak_topics(
        evaluation_result=evaluation_result,
        subject=subject,
    )
