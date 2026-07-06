"""
ADK Agent Skills Package
========================
Explicit skill functions for each agent domain.

Skills are callable async functions that encapsulate a single,
well-defined capability. Agents dispatch to these skills instead
of calling service classes directly, enabling:
  - Reuse across agents and MCP tools
  - Testability in isolation
  - Clean separation of capability from routing

Modules:
  physics_skills    - Physics SME skill functions
  chemistry_skills  - Chemistry SME skill functions
  evaluator_skills  - Teacher Review / Assessment skill functions
  rag_skills        - RAG retrieval skill functions
"""

from adk.skills.physics_skills import (
    explain_concept as physics_explain_concept,
    generate_summary as physics_generate_summary,
    generate_quick_notes as physics_generate_quick_notes,
    prepare_kcet as physics_prepare_kcet,
    prepare_neet as physics_prepare_neet,
    generate_formula_sheet,
)
from adk.skills.chemistry_skills import (
    explain_concept as chemistry_explain_concept,
    generate_summary as chemistry_generate_summary,
    generate_quick_notes as chemistry_generate_quick_notes,
    prepare_kcet as chemistry_prepare_kcet,
    prepare_neet as chemistry_prepare_neet,
    generate_equation_sheet,
)
from adk.skills.evaluator_skills import (
    evaluate_answer,
    evaluate_quiz,
    detect_weak_topics,
)
from adk.skills.rag_skills import (
    search_textbook,
    search_notes,
    search_exam_papers,
)
from adk.skills.progress_skill import get_progress_report, generate_revision_plan

__all__ = [
    # Physics skills
    "physics_explain_concept",
    "physics_generate_summary",
    "physics_generate_quick_notes",
    "physics_prepare_kcet",
    "physics_prepare_neet",
    "generate_formula_sheet",
    # Chemistry skills
    "chemistry_explain_concept",
    "chemistry_generate_summary",
    "chemistry_generate_quick_notes",
    "chemistry_prepare_kcet",
    "chemistry_prepare_neet",
    "generate_equation_sheet",
    # Evaluator skills
    "evaluate_answer",
    "evaluate_quiz",
    "detect_weak_topics",
    # RAG skills
    "search_textbook",
    "search_notes",
    "search_exam_papers",
    # Progress skill
    "get_progress_report",
    "generate_revision_plan",
]
