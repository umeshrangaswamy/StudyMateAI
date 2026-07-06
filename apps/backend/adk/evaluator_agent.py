"""
Evaluator ADK Agent
===================
ADK BaseAgent wrapper for the Teacher Review / Assessment domain.

Refactored to consume the Assessment MCP Server tools for evaluation and recommendation:
  - evaluate_answer
  - recommend_revision
"""

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from mcp_server.client import call_tool
        from adk.skills.evaluator_skills import evaluate_quiz

        state = ctx.session.state
        mode = state.get("evaluator_mode", "review")  # 'evaluate' | 'review'

        if mode == "evaluate":
            # ── Student Answer Grading via MCP ────────────────────────────────
            logger.info("EvaluatorAgent: executing in student grading mode via MCP.")
            questions = state.get("eval_questions", [])
            student_answers = state.get("eval_answers", {})
            subject = state.get("subject", "")
            exam = state.get("detected_exam")
            if exam == "none":
                exam = None

            # Grade answers via MCP tool
            eval_result = await call_tool(
                "assessment",
                "evaluate_answer",
                questions=questions,
                student_answers=student_answers,
                subject=subject,
                exam=exam,
            )
            state["evaluation_result"] = eval_result

            # Surface weak topics as revision recommendations via MCP tool
            weak_info = await call_tool(
                "assessment",
                "recommend_revision",
                evaluation_result=eval_result,
                subject=subject,
            )
            state["weak_topics"] = weak_info

            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Student answers evaluated.")],
                ),
            )

        else:
            # ── Quality Gate / Teacher Review ─────────────────────────────────
            logger.info("EvaluatorAgent: executing in response review mode.")
            query = state.get("query", "")
            response_text = state.get("response_text", "")
            subject = state.get("subject", "")
            intent = state.get("detected_intent", "doubt_solving")
            exam = state.get("detected_exam")
            if exam == "none":
                exam = None

            review_result = await evaluate_quiz(
                query=query,
                response_text=response_text,
                subject=subject,
                intent=intent,
                exam=exam,
                context=state.get("rag_chunks", []),
            )
            state["teacher_review"] = review_result

            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text="Response reviewed.")],
                ),
            )


def create_evaluator_agent():
    return EvaluatorAgent(name="evaluator_agent")

