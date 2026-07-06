"""
Progress Agent Skill
====================
Exposes student progress tracking and revision recommendations.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def get_progress_report(user_id: str) -> Dict[str, Any]:
    """
    Generate a detailed progress report and recommendations for a student.

    Args:
        user_id: Unique identifier for the student.

    Returns:
        Dict containing progress metrics, weak topics list, revision suggestions,
        readiness score, and a 7-day revision schedule.
    """
    logger.info(f"progress_skill: get_progress_report called for user={user_id}")
    from app.services.memory_service import MemoryService
    mem = MemoryService()

    progress = await mem.get_student_progress(user_id)

    # 1. Weak Topics Extraction
    weak_topics_dict = progress.get("weak_topics", {})
    all_weak_topics = [t for topics in weak_topics_dict.values() for t in topics]
    total_weak = len(all_weak_topics)

    # 2. Calculate Exam Readiness Score (WOW feature)
    # Starts at 100%. Deduct 10% per weak topic. Factor in quiz scores.
    readiness_score = 100
    readiness_score -= (total_weak * 10)

    quiz_scores = progress.get("quiz_scores", [])
    if quiz_scores:
        avg_score_ratio = sum(q.get("score", 0) / q.get("max_score", 1) for q in quiz_scores) / len(quiz_scores)
        # Factor average ratio into score (weighted average)
        readiness_score = int((readiness_score * 0.4) + (avg_score_ratio * 100 * 0.6))

    # Keep score bounded between 10% and 100%
    readiness_score = max(10, min(100, readiness_score))
    progress["readiness_score"] = readiness_score

    # 3. Generate Revision Advice & Planner (WOW feature)
    if total_weak == 0:
        advice = "Excellent work! Keep taking practice quizzes to maintain your standard."
        plan = {
            "Day 1-2": "Take a mock practice test.",
            "Day 3-5": "Review formula and equation sheets.",
            "Day 6-7": "Attempt NEET/KCET previous year questions."
        }
    else:
        advice = f"Focus your revision on your weak topics: {', '.join(all_weak_topics)}."
        # Distribute weak topics across a 7-day revision planner
        plan = {}
        for i, topic in enumerate(all_weak_topics):
            day_slot = f"Day {2*i + 1}-{2*i + 2}" if i < 3 else "Day 7"
            plan[day_slot] = f"Revise {topic} and attempt 5 practice questions."
        if "Day 7" not in plan:
            plan["Day 6-7"] = "Attempt a targeted NEET/KCET quiz on revised topics."

    progress["revision_advice"] = advice
    progress["revision_plan"] = plan

    return progress


async def generate_revision_plan(user_id: str) -> Dict[str, Any]:
    """
    Stand-alone revision planner generator.
    """
    logger.info(f"progress_skill: generate_revision_plan called for user={user_id}")
    report = await get_progress_report(user_id)
    return {
        "user_id": user_id,
        "revision_plan": report.get("revision_plan", {}),
        "readiness_score": report.get("readiness_score", 0)
    }
