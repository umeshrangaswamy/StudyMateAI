from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any

from app.agents.orchestrator import OrchestratorAgent
from app.agents.evaluator import TeacherReviewAgent
from app.models.request_models import AskRequest
from app.models.response_models import AskResponse

router = APIRouter()

@router.post("/api/ask", response_model=AskResponse, tags=["Academic"])
async def ask_endpoint(request: AskRequest):
    """
    Main academic doubt-solving, tutoring, quiz generation, and evaluation endpoint.
    Routes queries to the appropriate SME Agent or helper agent using curriculum-filtered context.
    """
    # Note: MVP subject check is now handled automatically by the Pydantic validator on AskRequest.
    orchestrator = OrchestratorAgent()
    try:
        response = await orchestrator.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator execution error: {str(e)}")

@router.get("/debug_rag", tags=["System"])
async def debug_rag(query: str, subject: str = "physics", exam: Optional[str] = None):
    from app.agents.rag_agent import RAGAgent
    rag = RAGAgent()
    try:
        res = await rag.retrieve(
            query=query,
            subject=subject,
            board="Karnataka State Board",
            year="2nd PUC",
            exam=exam
        )
        return res
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug_metadata", tags=["System"])
async def debug_metadata():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from app.core.config import settings
    try:
        conn = psycopg2.connect(settings.DATABASE_URL, connect_timeout=3)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT DISTINCT title FROM documents")
        docs = cursor.fetchall()
        cursor.execute("SELECT DISTINCT chapter FROM curriculum_chunks")
        chaps = cursor.fetchall()
        return {"documents": docs, "chapters": chaps}
    except Exception as e:
        return {"error": str(e)}

# --- System Liveness & Readiness Endpoints ---

@router.get("/health", tags=["System"])
def health_check():
    """Liveness check endpoint."""
    return {"status": "healthy", "service": "studymateai-backend"}

@router.get("/ready", tags=["System"])
def readiness_check():
    """Readiness check endpoint validating status of connected configurations and services."""
    # Under a production scenario, we would verify connections to Cloud SQL, Firestore, and Vertex AI.
    # Currently, return success as a placeholder.
    return {"status": "ready", "services": {"database": "configured", "vertex_ai": "ready", "firestore": "ready"}}


# --- Backward Compatibility Endpoints for /api/v1 prefix ---

@router.post("/api/v1/chat", response_model=AskResponse, tags=["Compatibility"])
async def compatibility_chat(request: AskRequest):
    return await ask_endpoint(request)

@router.post("/api/v1/quiz", tags=["Compatibility"])
async def compatibility_quiz(request: AskRequest):
    # Map AskRequest to process quiz generation
    orchestrator = OrchestratorAgent()
    try:
        res = await orchestrator.process_request(request, force_intent="quiz_generation")
        # Adapt output layout to match the old frontend layout expectation
        return {
            "questions": res.quiz_questions or [],
            "subject": res.metadata.subject,
            "exam": res.metadata.exam
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(e)}")

@router.post("/api/v1/evaluate", tags=["Compatibility"])
async def compatibility_evaluate(request: Dict[str, Any]):
    # Adapt raw compatibility dictionary payload to Evaluator inputs
    evaluator = TeacherReviewAgent()
    try:
        response = await evaluator.evaluate_answers(
            questions=request.get("questions", []),
            student_answers=request.get("student_answers", {}),
            subject=request.get("subject", "physics"),
            exam=request.get("exam")
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")
