import logging
import time
from typing import Optional, List, Dict, Any

from app.services.firestore_service import FirestoreService
from app.models.request_models import AskRequest
from app.models.response_models import (
    OrchestratorResult, SourceModel, MetadataModel,
    MCQQuestionModel, TeacherReviewModel, EvaluationModel
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Main Orchestrator Agent adapted to use the Google ADK architecture.
    Orchestrates RAG-grounding, SME processing, quiz generation, evaluation, and logging.
    """
    def __init__(self):
        self.firestore_service = FirestoreService()
        logger.info("OrchestratorAgent successfully instantiated.")

    async def process_request(self, request: AskRequest) -> OrchestratorResult:
        """
        Main entry point for unified query routing and multi-agent coordination.
        Runs the ADK Root Agent via Runner.
        """
        from app.core.logging import request_context_var
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        from adk.root_agent import create_root_agent

        start_time = time.perf_counter()
        agent_path = "root_agent"
        rag_chunks_found = 0
        error_type = None

        logger.info(f"Orchestrator received request for subject={request.subject}")

        # Set ContextVars
        request_context_var.set({
            "subject": request.subject,
            "board": request.board,
            "year": request.year,
        })

        try:
            # Create session
            session_service = InMemorySessionService()
            session_id = f"sess_{int(time.time())}"
            user_id = "default_student"

            initial_state = {
                "query": request.query,
                "subject": request.subject,
                "board": request.board,
                "year": request.year,
                "eval_questions": request.quiz_questions,
                "eval_answers": request.student_answers
            }

            await session_service.create_session(
                app_name="app",
                user_id=user_id,
                session_id=session_id,
                state=initial_state
            )

            # Build and execute ADK Root Agent
            root_agent = create_root_agent()
            runner = Runner(agent=root_agent, app_name="app", session_service=session_service)

            # Pass the user query as new_message to satisfy ADK runner requirements
            new_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=request.query or "")]
            )

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                pass

            # Retrieve updated session state
            session = await session_service.get_session(app_name="app", user_id=user_id, session_id=session_id)
            state = session.state

            # Read execution metadata
            agent_path = state.get("agent_path", "root_agent")
            intent = state.get("detected_intent", "doubt_solving")
            exam = state.get("detected_exam", "none")
            confidence = state.get("confidence", 0.90)
            response_text = state.get("response_text", "")

            # Format intent back to exam prep if appropriate
            if intent not in ["quiz_generation", "answer_evaluation", "lesson_summary", "quick_notes"] and exam in ["kcet", "neet"]:
                response_type = "explanation"
                intent = "entrance_preparation"
            elif intent == "quiz_generation":
                response_type = "quiz"
            elif intent == "answer_evaluation":
                response_type = "evaluation"
            elif intent == "lesson_summary":
                response_type = "summary"
            elif intent == "quick_notes":
                response_type = "notes"
            else:
                response_type = "explanation"

            # 4. Map RAG Sources
            rag_sources = state.get("rag_sources", [])
            rag_chunks_found = len(state.get("rag_chunks", []))
            sources = [
                SourceModel(
                    title=s.get("title", "Curriculum Document"),
                    chapter=s.get("chapter"),
                    page_number=s.get("page_number")
                ) for s in rag_sources
            ]

            # 5. Format Quiz Questions (if any)
            mcq_questions = []
            quiz_data = state.get("quiz_data")
            if quiz_data and "quiz" in quiz_data:
                for i, q in enumerate(quiz_data["quiz"], start=1):
                    opts = q.get("options", ["", "", "", ""])
                    mcq_questions.append(MCQQuestionModel(
                        id=i,
                        question=q["question"],
                        options={
                            "A": opts[0],
                            "B": opts[1],
                            "C": opts[2],
                            "D": opts[3]
                        },
                        correct_option=q["answer"],
                        explanation=q["explanation"]
                    ))

            # 6. Format Teacher Review (if any)
            teacher_review = None
            tr_dict = state.get("teacher_review")
            if tr_dict:
                teacher_review = TeacherReviewModel(
                    accuracy_score=tr_dict.get("accuracy_score", 0.95),
                    curriculum_alignment_score=tr_dict.get("curriculum_alignment_score", 0.98),
                    exam_alignment_score=tr_dict.get("exam_alignment_score", 0.92),
                    response_quality_score=tr_dict.get("response_quality_score", 0.94),
                    safety_score=tr_dict.get("safety_score", 1.0),
                    approved=tr_dict.get("approved", True),
                    feedback=tr_dict.get("feedback", "")
                )

            # 7. Format Evaluation (if any)
            evaluation = None
            eval_dict = state.get("evaluation_result")
            if eval_dict:
                evaluation = EvaluationModel(
                    score=eval_dict.get("score", 0),
                    max_score=eval_dict.get("max_score", 0),
                    feedback=eval_dict.get("feedback", ""),
                    missing_points=eval_dict.get("missing_points", []),
                    revision_tip=eval_dict.get("revision_tip", "")
                )

            # Log transaction in Firestore
            await self.firestore_service.log_query_transaction(
                year_of_study=request.year,
                board=request.board,
                subject=request.subject,
                prompt=request.query,
                intent=intent,
                response_text=response_text
            )

            return OrchestratorResult(
                answer=response_text,
                response_type=response_type,
                sources=sources,
                metadata=MetadataModel(
                    subject=request.subject,
                    intent=intent,
                    exam=exam if exam != "none" else None,
                    confidence=confidence
                ),
                quiz_questions=mcq_questions or None,
                teacher_review=teacher_review,
                evaluation=evaluation
            )

        except Exception as e:
            error_type = type(e).__name__
            logger.error(
                f"Exception during orchestrator process execution: {str(e)}",
                extra={
                    "error_type": error_type
                }
            )
            raise e

        finally:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                f"Agent execution completed in {latency_ms:.2f}ms",
                extra={
                    "agent_path": agent_path,
                    "rag_chunks_found": rag_chunks_found,
                    "latency_ms": latency_ms,
                    "model_name": settings.MODEL_NAME,
                    "error_type": error_type or "none"
                }
            )
