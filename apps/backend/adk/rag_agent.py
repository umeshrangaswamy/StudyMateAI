"""
RAG ADK Agent
=============
ADK BaseAgent wrapper for the RAG retrieval domain.

Refactored to consume the Knowledge MCP Server tools instead of
direct skill calls:
  - search_curriculum
  - get_notes
  - get_previous_questions
"""

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from mcp_server.client import call_tool

        state = ctx.session.state
        query = state.get("query") or ""
        subject = state.get("subject") or ""
        board = state.get("board") or ""
        year = state.get("year") or ""
        intent = state.get("detected_intent") or "doubt_solving"
        exam = state.get("detected_exam")

        # Normalise exam value
        if exam == "none":
            exam = None

        logger.info(
            f"RAGAgent dispatching retrieval via MCP for intent={intent}, exam={exam}"
        )

        try:
            if intent in ("quick_notes", "lesson_summary"):
                # Notes-oriented retrieval via MCP get_notes tool
                res = await call_tool(
                    "knowledge",
                    "get_notes",
                    query=query,
                    subject=subject,
                    board=board,
                    year=year,
                    exam=exam,
                )
            elif exam in ("kcet", "neet"):
                # Entrance-exam retrieval via MCP get_previous_questions tool
                res = await call_tool(
                    "knowledge",
                    "get_previous_questions",
                    query=query,
                    subject=subject,
                    board=board,
                    year=year,
                    exam=exam,
                )
            else:
                # General textbook retrieval via MCP search_curriculum tool
                res = await call_tool(
                    "knowledge",
                    "search_curriculum",
                    query=query,
                    subject=subject,
                    board=board,
                    year=year,
                    exam=exam,
                )
        except Exception as exc:
            # Fall back gracefully to search_curriculum
            logger.warning(
                f"RAGAgent MCP retrieval error (falling back to search_curriculum): {exc}"
            )
            res = await call_tool(
                "knowledge",
                "search_curriculum",
                query=query,
                subject=subject,
                board=board,
                year=year,
                exam=None,
            )

        state["rag_chunks"] = res["chunks"]
        state["rag_sources"] = res["sources"]

        msg = f"Retrieved {len(res['chunks'])} chunks."
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text=msg)],
            ),
        )


def create_rag_agent():
    return RAGAgent(name="rag_agent")

