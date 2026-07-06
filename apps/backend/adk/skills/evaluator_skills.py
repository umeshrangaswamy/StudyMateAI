"""
Evaluator Agent Skills
======================
Explicit skill functions for the Teacher Review / Assessment domain.

Skills encapsulate the two modes of the TeacherReviewAgent:
  - evaluate_answer  : Grade student answers (MCQ exact-match or subjective LLM)
  - evaluate_quiz    : Review LLM-generated quiz or SME response for quality
  - detect_weak_topics: Post-process an evaluation result to surface weak areas

Skills are called by:
  - EvaluatorAgent (ADK) for direct dispatch
  - assessment_server (MCP) via evaluate_answer and recommend_revision
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def evaluate_answer(
    questions: List[Dict[str, Any]],
    student_answers: Dict[str, str],
    subject: str,
    exam: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate student quiz answers or subjective explanations.

    Applies exact-match grading for MCQ answer keys when present,
    and delegates to Gemini Flash for subjective/conceptual reasoning.

    Args:
        questions:       List of question dicts with 'id', 'question',
                         'correct_option', and 'explanation' keys.
        student_answers: Map of question id (str) → student selected option.
        subject:         Academic subject ('physics' or 'chemistry').
        exam:            Optional entrance exam ('kcet' or 'neet').

    Returns:
        EvaluationModel-compatible dict with keys:
          score, max_score, feedback, missing_points, revision_tip
    """
    logger.info(
        f"evaluator_skill: evaluate_answer called, subject={subject}, exam={exam}"
    )
    from app.agents.evaluator import TeacherReviewAgent
    agent = TeacherReviewAgent()
    result = await agent.evaluate_answers(
        questions=questions,
        student_answers=student_answers,
        subject=subject,
        exam=exam,
    )
    return result.model_dump()


async def evaluate_quiz(
    query: str,
    response_text: str,
    subject: str,
    intent: str,
    exam: Optional[str] = None,
    context: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Review a generated SME response or quiz for academic quality.

    Checks factual accuracy, curriculum alignment, exam alignment,
    response quality, and safety guardrails. Returns structured
    approval status and feedback.

    Args:
        query:         Original student query.
        response_text: Generated SME response or formatted quiz text.
        subject:       Academic subject.
        intent:        Detected intent (e.g. 'quiz_generation', 'lesson_summary').
        exam:          Optional entrance exam focus.
        context:       Optional list of RAG chunks used in the response.

    Returns:
        TeacherReviewModel-compatible dict with keys:
          accuracy_score, curriculum_alignment_score, exam_alignment_score,
          response_quality_score, approved, feedback
    """
    logger.info(
        f"evaluator_skill: evaluate_quiz called, subject={subject}, intent={intent}, exam={exam}"
    )
    from app.agents.evaluator import TeacherReviewAgent
    agent = TeacherReviewAgent()
    result = await agent.review_response(
        query=query,
        response_text=response_text,
        subject=subject,
        intent=intent,
        exam=exam,
        context=context or [],
    )
    return result.model_dump()


async def detect_weak_topics(
    evaluation_result: Dict[str, Any],
    subject: str,
) -> Dict[str, Any]:
    """
    Identify weak topics from an evaluation result.

    Analyses the missing_points field of a completed evaluation and
    extracts topic-level weakness signals. Returns a structured
    revision recommendation that agents and MCP clients can surface
    to students.

    Args:
        evaluation_result: Output dict from evaluate_answer skill,
                           containing score, missing_points, revision_tip.
        subject:           Academic subject for context.

    Returns:
        Dict with keys:
          weak_topics    (list[str])  - distinct topic labels
          revision_tips  (list[str])  - actionable revision suggestions
          priority       (str)        - 'high' | 'medium' | 'low'
    """
    logger.info(
        f"evaluator_skill: detect_weak_topics called, subject={subject}"
    )
    score = evaluation_result.get("score", 0)
    max_score = evaluation_result.get("max_score", 1)
    missing_points = evaluation_result.get("missing_points", [])
    revision_tip = evaluation_result.get("revision_tip", "")

    # Derive priority from score ratio
    ratio = score / max_score if max_score > 0 else 0.0
    if ratio < 0.4:
        priority = "high"
    elif ratio < 0.7:
        priority = "medium"
    else:
        priority = "low"

    # Extract unique topic labels from missing_points strings
    weak_topics: List[str] = []
    for point in missing_points:
        # Each point is a teacher-generated sentence — extract first clause
        topic_label = point.split(":")[0].strip() if ":" in point else point[:60].strip()
        if topic_label and topic_label not in weak_topics:
            weak_topics.append(topic_label)

    revision_tips: List[str] = [revision_tip] if revision_tip else []
    if not revision_tips and weak_topics:
        revision_tips = [
            f"Review {subject} curriculum chapters covering: {', '.join(weak_topics[:3])}."
        ]

    return {
        "weak_topics": weak_topics,
        "revision_tips": revision_tips,
        "priority": priority,
        "score": score,
        "max_score": max_score,
    }
