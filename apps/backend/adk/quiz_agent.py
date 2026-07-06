import logging
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)

class QuizAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        year = state.get("year")
        board = state.get("board")
        subject = state.get("subject")
        query = state.get("query")
        exam = state.get("detected_exam")
        chunks = state.get("rag_chunks", [])

        if exam == "none":
            exam = None

        logger.info(f"QuizAgent generating MCQs for subject={subject} via MCP")

        from mcp_server.client import call_tool
        # Execute generation via MCP tool call
        quiz_data = await call_tool(
            "assessment",
            "generate_quiz",
            year=year,
            board=board,
            subject=subject,
            query=query,
            exam=exam,
            chunks=chunks
        )

        state["quiz_data"] = quiz_data
        yield Event(
            author=self.name,
            content=types.Content(role="model", parts=[types.Part.from_text(text="Quiz generation complete.")])
        )

def create_quiz_agent():
    return QuizAgent(name="quiz_agent")

