"""
Chemistry ADK Agent
===================
ADK BaseAgent wrapper for the Chemistry SME domain.

Dispatches to explicit chemistry skill functions based on the
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
  (equation queries)  → generate_equation_sheet
"""

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)


class ChemistryAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from adk.skills.chemistry_skills import (
            explain_concept,
            generate_summary,
            generate_quick_notes,
            prepare_kcet,
            prepare_neet,
            generate_equation_sheet,
        )

        state = ctx.session.state
        query = state.get("query") or ""
        intent = state.get("detected_intent") or "doubt_solving"
        exam = state.get("detected_exam")
        context = state.get("rag_chunks", [])
        response_style = state.get("response_style", "concise")

        # Normalise exam value
        if exam == "none":
            exam = None

        logger.info(
            f"ChemistryAgent dispatching skill for intent={intent}, exam={exam}, response_style={response_style}"
        )

        # Detect equation-sheet requests by query keywords
        query_lower = query.lower()
        if any(
            w in query_lower
            for w in ["equation sheet", "reaction sheet", "all equations", "all reactions"]
        ):
            res = await generate_equation_sheet(
                query=query, context=context, exam=exam, response_style=response_style
            )

        elif intent == "entrance_preparation":
            if exam == "neet":
                res = await prepare_neet(query=query, context=context, response_style=response_style)
            else:
                res = await prepare_kcet(query=query, context=context, response_style=response_style)

        elif intent == "lesson_summary":
            res = await generate_summary(
                query=query, context=context, exam=exam, response_style=response_style
            )

        elif intent == "quick_notes":
            res = await generate_quick_notes(
                query=query, context=context, exam=exam, response_style=response_style
            )

        else:
            # Default: explain_concept covers lesson_explanation,
            # doubt_solving, exam_preparation
            res = await explain_concept(
                query=query, context=context, exam=exam, response_style=response_style
            )

        state["chemistry_response"] = res
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text=res or "")],
            ),
        )


def create_chemistry_agent():
    return ChemistryAgent(name="chemistry_agent")
