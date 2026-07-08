import logging
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types

logger = logging.getLogger(__name__)

class RootAgent(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        from app.security.prompt_guard import PromptGuard
        prompt_guard = PromptGuard()
        from adk.rag_agent import create_rag_agent
        from adk.physics_agent import create_physics_agent
        from adk.chemistry_agent import create_chemistry_agent
        from adk.quiz_agent import create_quiz_agent
        from adk.evaluator_agent import create_evaluator_agent

        state = ctx.session.state
        query = state.get("query") or ""
        subject = (state.get("subject") or "").lower()
        board = state.get("board")
        year = state.get("year")

        logger.info(f"RootAgent executing request for subject={subject}")

        # 1. Security Check via Prompt Guard
        guard_status = prompt_guard.validate_prompt(query)
        if not guard_status["allowed"]:
            logger.warning(f"Request blocked by prompt guard: {guard_status.get('reason')}")
            state["is_blocked"] = True
            state["agent_path"] = "root_agent -> prompt_guard"
            state["response_text"] = "I cannot answer this query. It violates curriculum safety and design boundaries."
            state["detected_intent"] = "blocked"
            state["detected_exam"] = self._detect_exam(query)
            state["confidence"] = 0.0
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={
                    "is_blocked": True,
                    "agent_path": "root_agent -> prompt_guard",
                    "response_text": state["response_text"],
                    "detected_intent": "blocked",
                    "detected_exam": state["detected_exam"],
                    "confidence": 0.0
                }),
                content=types.Content(role="model", parts=[types.Part.from_text(text=state["response_text"])])
            )
            return

        # 2. Intent and Exam Detection
        force_intent = state.get("force_intent")
        if force_intent:
            intent = force_intent
        else:
            intent = self._detect_intent(query, subject, bool(state.get("eval_answers")))
        exam = self._detect_exam(query)

        state["detected_intent"] = intent
        state["detected_exam"] = exam
        state["is_blocked"] = False

        # Instantiate sub-agents
        rag_agent = create_rag_agent()
        quiz_agent = create_quiz_agent()
        evaluator_agent = create_evaluator_agent()

        # 3. Route Workflows
        if intent == "quiz_generation":
            state["agent_path"] = "root_agent -> RAG -> QuizAgent"
            # Execute RAG
            async for ev in rag_agent.run_async(ctx):
                yield ev
            # Execute Quiz Generation
            async for ev in quiz_agent.run_async(ctx):
                yield ev

            # Format quiz text for review
            quiz_data = state.get("quiz_data", {})
            quiz_list = quiz_data.get("quiz", [])
            quiz_text = ""
            for i, q in enumerate(quiz_list, start=1):
                opts = q.get("options", ["", "", "", ""])
                quiz_text += (
                    f"Question {i}: {q.get('question')}\n"
                    f"Options: A) {opts[0]}, B) {opts[1]}, C) {opts[2]}, D) {opts[3]}\n"
                    f"Correct Answer: {q.get('answer')}\n"
                    f"Explanation: {q.get('explanation')}\n"
                )

            # Mandatory Quiz Quality Review
            state["response_text"] = quiz_text
            state["evaluator_mode"] = "review"
            state["agent_path"] += " -> EvaluatorAgent"
            async for ev in evaluator_agent.run_async(ctx):
                yield ev

        elif intent == "answer_evaluation":
            state["agent_path"] = "root_agent -> EvaluatorAgent"
            # Fetch context and quiz questions first if not available
            if not state.get("eval_questions"):
                # Save previous intent
                old_intent = state.get("detected_intent")
                state["detected_intent"] = "quiz_generation"
                async for ev in rag_agent.run_async(ctx):
                    yield ev
                async for ev in quiz_agent.run_async(ctx):
                    yield ev
                state["detected_intent"] = old_intent
                # Adapt generated questions
                gen_questions = []
                quiz_list = state.get("quiz_data", {}).get("quiz", [])
                for i, q in enumerate(quiz_list, start=1):
                    opts = q.get("options", ["", "", "", ""])
                    gen_questions.append({
                        "id": i,
                        "question": q["question"],
                        "options": {"A": opts[0], "B": opts[1], "C": opts[2], "D": opts[3]},
                        "correct_option": q["answer"],
                        "explanation": q["explanation"]
                    })
                state["eval_questions"] = gen_questions

            state["evaluator_mode"] = "evaluate"
            async for ev in evaluator_agent.run_async(ctx):
                yield ev
            state["response_text"] = state.get("evaluation_result", {}).get("feedback", "")

        else:
            # doubt_solving / learning workflow (RAG + SME)
            if subject == "physics":
                state["agent_path"] = "root_agent -> RAG -> PhysicsAgent"
                sme_agent = create_physics_agent()
            elif subject == "chemistry":
                state["agent_path"] = "root_agent -> RAG -> ChemistryAgent"
                sme_agent = create_chemistry_agent()
            else:
                state["response_text"] = f"Subject '{subject}' is not supported in the MVP."
                yield Event(
                    author=self.name,
                    content=types.Content(role="model", parts=[types.Part.from_text(text=state["response_text"])])
                )
                return

            # Execute RAG
            async for ev in rag_agent.run_async(ctx):
                yield ev

            # Execute SME Agent
            async for ev in sme_agent.run_async(ctx):
                yield ev

            # Fetch the generated SME response
            response_text = state.get("physics_response" if subject == "physics" else "chemistry_response", "")
            state["response_text"] = response_text

            # Routing rules logic for quality validation
            CONFIDENCE_THRESHOLD = 0.85
            confidence = self._calculate_confidence(query, intent, exam)
            state["confidence"] = confidence

            evaluator_required = False
            if exam in ["kcet", "neet"]:
                evaluator_required = True
            elif intent in ["lesson_summary", "quick_notes"]:
                evaluator_required = True
            elif confidence < CONFIDENCE_THRESHOLD:
                evaluator_required = True

            if evaluator_required:
                state["evaluator_mode"] = "review"
                state["agent_path"] += " -> EvaluatorAgent"
                async for ev in evaluator_agent.run_async(ctx):
                    yield ev

                # Gatekeeper check: if rejected, update output message with feedback details
                teacher_review = state.get("teacher_review", {})
                if teacher_review and not teacher_review.get("approved", True):
                    state["response_text"] = f"Review Alert: This generated response did not pass the academic quality check. Reason: {teacher_review.get('feedback')}"

        # Build final state delta to persist results back to session store
        final_state_delta = {
            k: state.get(k)
            for k in [
                "response_text", "detected_intent", "detected_exam", "confidence",
                "agent_path", "is_blocked", "rag_chunks", "rag_sources",
                "quiz_data", "teacher_review", "evaluation_result"
            ]
            if state.get(k) is not None
        }

        yield Event(
            author=self.name,
            actions=EventActions(state_delta=final_state_delta),
            content=types.Content(role="model", parts=[types.Part.from_text(text=state.get("response_text", ""))])
        )

    def _detect_intent(self, query: str, subject: str, has_student_answers: bool) -> str:
        if has_student_answers:
            return "answer_evaluation"
            
        q_lower = query.lower()
        if any(w in q_lower for w in ["quiz", "test", "assess"]):
            return "quiz_generation"
        elif any(w in q_lower for w in ["evaluate", "grade"]):
            return "answer_evaluation"
        elif any(w in q_lower for w in ["neet", "kcet"]):
            return "entrance_preparation"
        elif any(w in q_lower for w in ["summary", "summarize"]):
            return "lesson_summary"
        elif any(w in q_lower for w in ["notes", "revision"]):
            return "quick_notes"
        elif any(w in q_lower for w in ["explain", "what is"]):
            return "lesson_explanation"
        elif any(w in q_lower for w in ["exam", "prep", "solve"]):
            return "exam_preparation"
        return "doubt_solving"

    def _detect_exam(self, query: str) -> str:
        q_upper = query.upper()
        if "NEET" in q_upper:
            return "neet"
        elif "KCET" in q_upper:
            return "kcet"
        return "none"

    def _calculate_confidence(self, query: str, intent: str, exam: str) -> float:
        confidence = 0.86
        query_lower = query.lower()
        if len(query_lower) < 15:
            confidence = 0.75
        elif any(word in query_lower for word in ["unsure", "not sure", "maybe", "approximate", "guess"]):
            confidence = 0.80
        return confidence

def create_root_agent():
    return RootAgent(name="root_agent")
