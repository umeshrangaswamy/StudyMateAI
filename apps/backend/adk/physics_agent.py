"""
Physics ADK Agent
=================
ADK BaseAgent wrapper for the Physics SME domain.

Dispatches to explicit physics skill functions based on the
detected intent stored in session state. This replaces the
previous monolithic `generate_response(intent=intent)` call
with named skill dispatch, making each capability testable
and reusable by the MCP layer.

Skill dispatch map:
  lesson_explanation  → explain_concept
  lesson_summary      → generate_summary
  quick_notes         → generate_quick_notes
  entrance_preparation (kcet) → prepare_kcet
  entrance_preparation (neet) → prepare_neet
  exam_preparation    → explain_concept (exam-focused)
  doubt_solving       → explain_concept (default)
  (formula queries)   → generate_formula_sheet
"""

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)

# Intent → skill name map
_INTENT_SKILL_MAP = {
    "lesson_explanation": "explain_concept",
    "lesson_summary": "generate_summary",
    "quick_notes": "generate_quick_notes",
    "doubt_solving": "explain_concept",
    "exam_preparation": "explain_concept",
    "entrance_preparation": "prepare_kcet",  # refined by exam below
}


class PhysicsAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from adk.skills.physics_skills import (
            explain_concept,
            generate_summary,
            generate_quick_notes,
            prepare_kcet,
            prepare_neet,
            generate_formula_sheet,
        )

        state = ctx.session.state
        query = state.get("query") or ""
        intent = state.get("detected_intent") or "doubt_solving"
        exam = state.get("detected_exam")
        context = state.get("rag_chunks", [])

        # Normalise exam value
        if exam == "none":
            exam = None

        logger.info(
            f"PhysicsAgent dispatching skill for intent={intent}, exam={exam}"
        )

        # Detect formula-sheet requests by query keywords
        query_lower = query.lower()
        if any(w in query_lower for w in ["formula", "formulae", "formula sheet"]):
            res = await generate_formula_sheet(
                query=query, context=context, exam=exam
            )

        elif intent == "entrance_preparation":
            if exam == "neet":
                res = await prepare_neet(query=query, context=context)
            else:
                res = await prepare_kcet(query=query, context=context)

        elif intent == "lesson_summary":
            res = await generate_summary(
                query=query, context=context, exam=exam
            )

        elif intent == "quick_notes":
            res = await generate_quick_notes(
                query=query, context=context, exam=exam
            )

        else:
            # Default: explain_concept covers lesson_explanation,
            # doubt_solving, exam_preparation
            res = await explain_concept(
                query=query, context=context, exam=exam
            )

        state["physics_response"] = res
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text=res or "")],
            ),
        )


def create_physics_agent():
    return PhysicsAgent(name="physics_agent")
