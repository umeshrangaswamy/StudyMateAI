import logging
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

async def generate_mcq_quiz(
    year: str,
    board: str,
    subject: str,
    query: str,
    exam: Optional[str] = None,
    chunks: Optional[List[str]] = None,
    tool_context: Optional[ToolContext] = None
) -> Dict[str, Any]:
    """
    Generates a multiple-choice question quiz based on academic context.

    Args:
        year: Year of study.
        board: University / Board.
        subject: Subject (physics or chemistry).
        query: User query / intent details.
        exam: Optional entrance exam name (kcet or neet).
        chunks: Optional list of retrieved context chunks.

    Returns:
        A dictionary containing the generated 'quiz' list.
    """
    logger.info(f"ADK quiz_tool called for subject={subject}, exam={exam}")
    from app.agents.quiz_generator import QuizGeneratorAgent

    quiz_generator = QuizGeneratorAgent()
    quiz_data = await quiz_generator.generate_quiz(
        year=year,
        board=board,
        subject=subject,
        query=query,
        exam=exam,
        context=chunks or [],
        sources=[]
    )
    return quiz_data
