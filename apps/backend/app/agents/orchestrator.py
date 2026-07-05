import logging
from typing import Optional, List, Dict, Any
from app.security.prompt_guard import PromptGuard
from app.agents.rag_agent import RAGAgent
from app.agents.physics_sme import PhysicsSMEAgent
from app.agents.chemistry_sme import ChemistrySMEAgent
from app.agents.quiz_generator import QuizGeneratorAgent
from app.agents.evaluator import EvaluatorAgent
from app.services.firestore_service import FirestoreService
from app.models.request_models import AskRequest
from app.models.response_models import OrchestratorResult, SourceModel, MetadataModel, MCQQuestionModel, TeacherReviewModel

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Main Orchestrator Agent. Manages security validation, intent routing,
    RAG-grounding, SME processing, quiz generation, evaluation, and logging.
    """
    def __init__(self):
        self.prompt_guard = PromptGuard()
        self.rag_agent = RAGAgent()
        self.physics_sme = PhysicsSMEAgent()
        self.chemistry_sme = ChemistrySMEAgent()
        self.quiz_generator = QuizGeneratorAgent()
        self.evaluator = EvaluatorAgent()
        self.firestore_service = FirestoreService()
        logger.info("OrchestratorAgent successfully instantiated.")

    async def process_request(self, request: AskRequest) -> OrchestratorResult:
        """
        Main entry point for unified query routing and multi-agent coordination.
        Runs rule-based Prompt Guard safety check before any model/service call.
        """
        import time
        from app.core.logging import request_context_var
        from app.core.config import settings

        start_time = time.perf_counter()
        agent_path = "orchestrator"
        rag_chunks_found = 0
        error_type = None

        logger.info(f"Orchestrator received request for subject={request.subject}")

        # Set basic ContextVars parameters (preventing raw query logs to protect student PII)
        request_context_var.set({
            "subject": request.subject,
            "board": request.board,
            "year": request.year,
        })

        try:
            # 1. Security Check via Prompt Guard (Before ANY model or service calls)
            guard_status = self.prompt_guard.validate_prompt(request.query)
            if not guard_status["allowed"]:
                agent_path = "orchestrator -> prompt_guard"
                logger.warning(f"Request blocked by prompt guard. Reason: {guard_status.get('reason')}")
                return OrchestratorResult(
                    answer="I cannot answer this query. It violates curriculum safety and design boundaries.",
                    response_type="explanation",
                    sources=[],
                    metadata=MetadataModel(
                        subject=request.subject,
                        intent="blocked",
                        exam=self._detect_exam(request.query),
                        confidence=0.0
                    )
                )

            # 2. Intent and Exam Detection
            intent = self._detect_intent(request)
            exam = self._detect_exam(request.query)
            
            # Enrich context variables
            request_context_var.set({
                "subject": request.subject,
                "board": request.board,
                "year": request.year,
                "detected_intent": intent,
                "detected_exam": exam or "none",
            })

            # Map intent to response_type
            if intent == "quiz_generation":
                response_type = "quiz"
            elif intent == "answer_evaluation":
                response_type = "evaluation"
            elif intent == "lesson_summary":
                response_type = "summary"
            elif intent == "quick_notes":
                response_type = "notes"
            else:
                response_type = "explanation"

            # 3. Route workflow based on intent
            if intent == "quiz_generation":
                agent_path = "orchestrator -> RAG -> QuizGenerator"
                rag_result = await self.rag_agent.retrieve(
                    query=request.query,
                    subject=request.subject,
                    board=request.board,
                    year=request.year,
                    exam=exam
                )
                rag_chunks_found = len(rag_result.get("chunks", []))
                
                quiz_data = await self.quiz_generator.generate_quiz(
                    year=request.year,
                    board=request.board,
                    subject=request.subject,
                    query=request.query,
                    exam=exam,
                    context=rag_result["chunks"],
                    sources=rag_result["sources"]
                )
                
                # Reconstruct quiz list into MCQQuestionModel list for backward compatibility
                mcq_questions = []
                for i, q in enumerate(quiz_data["quiz"], start=1):
                    mcq_questions.append(MCQQuestionModel(
                        id=i,
                        question=q["question"],
                        options={
                            "A": q["options"][0],
                            "B": q["options"][1],
                            "C": q["options"][2],
                            "D": q["options"][3]
                        },
                        correct_option=q["answer"],
                        explanation=q["explanation"]
                    ))

                # Citations for the quiz
                sources = [
                    SourceModel(
                        title=s.get("title", "Curriculum Document"),
                        chapter=s.get("chapter"),
                        page_number=s.get("page_number")
                    ) for s in rag_result["sources"]
                ]

                # Mandatory quiz review
                agent_path += " -> EvaluatorReview"
                quiz_text = "\n".join([
                    f"Question {q.id}: {q.question}\n"
                    f"Options: A) {q.options['A']}, B) {q.options['B']}, C) {q.options['C']}, D) {q.options['D']}\n"
                    f"Correct Answer: {q.correct_option}\n"
                    f"Explanation: {q.explanation}"
                    for q in mcq_questions
                ])
                teacher_review = await self.evaluator.review_response(
                    query=request.query,
                    response_text=quiz_text,
                    subject=request.subject,
                    intent=intent,
                    exam=exam,
                    context=rag_result["chunks"]
                )

                return OrchestratorResult(
                    answer=f"Generated quiz with {len(mcq_questions)} questions.",
                    response_type=response_type,
                    sources=sources,
                    metadata=MetadataModel(
                        subject=request.subject,
                        intent=intent,
                        exam=exam,
                        confidence=0.86
                    ),
                    quiz_questions=mcq_questions,
                    teacher_review=teacher_review
                )

            elif intent == "answer_evaluation":
                agent_path = "orchestrator -> Evaluator"
                # Safely get questions and answers
                questions_list = request.quiz_questions or []
                if not questions_list:
                    # Build mock fallback questions using RAG
                    rag_result = await self.rag_agent.retrieve(
                        query=request.query,
                        subject=request.subject,
                        board=request.board,
                        year=request.year,
                        exam=exam
                    )
                    rag_chunks_found = len(rag_result.get("chunks", []))
                    
                    quiz_data = await self.quiz_generator.generate_quiz(
                        year=request.year,
                        board=request.board,
                        subject=request.subject,
                        query=request.query,
                        exam=exam,
                        context=rag_result["chunks"],
                        sources=rag_result["sources"]
                    )
                    questions_list = []
                    for i, q in enumerate(quiz_data["quiz"], start=1):
                        questions_list.append({
                            "id": i,
                            "question": q["question"],
                            "options": {
                                "A": q["options"][0],
                                "B": q["options"][1],
                                "C": q["options"][2],
                                "D": q["options"][3]
                            },
                            "correct_option": q["answer"],
                            "explanation": q["explanation"]
                        })
                
                student_answers = request.student_answers or {}
                evaluation_res = await self.evaluator.evaluate_answers(
                    questions=questions_list,
                    student_answers=student_answers,
                    subject=request.subject,
                    exam=exam
                )
                return OrchestratorResult(
                    answer=evaluation_res.feedback,
                    response_type=response_type,
                    sources=[],
                    metadata=MetadataModel(
                        subject=request.subject,
                        intent=intent,
                        exam=exam,
                        confidence=0.86
                    ),
                    evaluation=evaluation_res
                )

            else:
                # Default doubt_solving / learning workflow (RAG + SME)
                if request.subject.lower() == "physics":
                    agent_path = "orchestrator -> RAG -> PhysicsSME"
                elif request.subject.lower() == "chemistry":
                    agent_path = "orchestrator -> RAG -> ChemistrySME"
                else:
                    agent_path = "orchestrator -> UnsupportedSME"

                # Retrieve grounding sources
                rag_result = await self.rag_agent.retrieve(
                    query=request.query,
                    subject=request.subject,
                    board=request.board,
                    year=request.year,
                    exam=exam
                )
                rag_chunks_found = len(rag_result.get("chunks", []))

                # Invoke domain SME
                if request.subject.lower() == "physics":
                    response_text = await self.physics_sme.generate_response(
                        prompt=request.query,
                        intent=intent,
                        exam=exam,
                        context=rag_result["chunks"]
                    )
                elif request.subject.lower() == "chemistry":
                    response_text = await self.chemistry_sme.generate_response(
                        prompt=request.query,
                        intent=intent,
                        exam=exam,
                        context=rag_result["chunks"]
                    )
                else:
                    response_text = f"Subject '{request.subject}' is not supported in the Free Tier."

                # Routing rules logic for quality validation
                CONFIDENCE_THRESHOLD = 0.85
                confidence = self._calculate_confidence(request, intent, exam)

                evaluator_required = False
                if exam in ["kcet", "neet"]:
                    evaluator_required = True
                elif intent in ["lesson_summary", "quick_notes"]:
                    evaluator_required = True
                elif confidence < CONFIDENCE_THRESHOLD:
                    evaluator_required = True

                teacher_review = None
                if evaluator_required:
                    agent_path += " -> EvaluatorReview"
                    teacher_review = await self.evaluator.review_response(
                        query=request.query,
                        response_text=response_text,
                        subject=request.subject,
                        intent=intent,
                        exam=exam,
                        context=rag_result["chunks"]
                    )
                    
                    # Gatekeeper check: if rejected, update output message with feedback details
                    if teacher_review and not teacher_review.approved:
                        response_text = f"Review Alert: This generated response did not pass the academic quality check. Reason: {teacher_review.feedback}"

                # Structure grounding sources metadata
                sources = [
                    SourceModel(
                        title=s.get("title", "Curriculum Document"),
                        chapter=s.get("chapter"),
                        page_number=s.get("page_number")
                    ) for s in rag_result["sources"]
                ]

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
                        exam=exam,
                        confidence=confidence
                    ),
                    teacher_review=teacher_review
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
            
            # Log structured agent transaction metadata
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

    def _detect_intent(self, request: AskRequest) -> str:
        """
        Determines the student's request intent deterministically.
        """
        if getattr(request, "student_answers", None) is not None:
            return "answer_evaluation"
            
        prompt_lower = request.query.lower()
        if "quiz" in prompt_lower or "test" in prompt_lower or "assess" in prompt_lower:
            return "quiz_generation"
        elif "evaluate" in prompt_lower or "grade" in prompt_lower:
            return "answer_evaluation"
        elif "neet" in prompt_lower or "kcet" in prompt_lower:
            return "entrance_preparation"
        elif "summary" in prompt_lower or "summarize" in prompt_lower:
            return "lesson_summary"
        elif "notes" in prompt_lower or "revision" in prompt_lower:
            return "quick_notes"
        elif "explain" in prompt_lower or "what is" in prompt_lower:
            return "lesson_explanation"
        elif "exam" in prompt_lower or "prep" in prompt_lower or "solve" in prompt_lower:
            return "exam_preparation"
        return "doubt_solving"


    def _detect_exam(self, prompt: str) -> Optional[str]:
        """
        Detects selected entrance exams within scope parameters.
        """
        prompt_upper = prompt.upper()
        if "NEET" in prompt_upper:
            return "neet"
        elif "KCET" in prompt_upper:
            return "kcet"
        return None

    def _calculate_confidence(self, request: AskRequest, intent: str, exam: Optional[str]) -> float:
        """
        Determines the routing/classification confidence.
        Returns a value below 0.85 if the query is vague/low-confidence.
        """
        confidence = 0.86
        query_lower = request.query.lower()
        
        # Condition 1: Extremely short queries (often vague or incomplete)
        if len(query_lower) < 15:
            confidence = 0.75
        # Condition 2: Keyword indicators of doubt/uncertainty
        elif any(word in query_lower for word in ["unsure", "not sure", "maybe", "approximate", "guess"]):
            confidence = 0.80
            
        return confidence
