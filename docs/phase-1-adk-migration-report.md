# Phase 1: Google ADK Migration Report

## Overview

Phase 1 migrates the StudyMateAI backend from a monolithic orchestrator pattern to a 
Google Agent Development Kit (ADK) multi-agent architecture. The migration preserves all 
existing API contracts and Cloud Run deployment configurations while introducing structured 
agent hierarchy, tool-based retrieval, and a session-managed Runner pipeline.

---

## Files Created

| File | Purpose |
|------|---------|
| `apps/backend/adk/__init__.py` | ADK namespace entry point exposing all agent factories |
| `apps/backend/adk/root_agent.py` | Root coordination agent; handles intent routing, exam detection, prompt guard, and conditional evaluator gating |
| `apps/backend/adk/physics_agent.py` | Physics SME BaseAgent wrapper calling PhysicsSMEAgent.generate_response |
| `apps/backend/adk/chemistry_agent.py` | Chemistry SME BaseAgent wrapper calling ChemistrySMEAgent.generate_response |
| `apps/backend/adk/rag_agent.py` | RAG BaseAgent wrapper calling retrieve_curriculum_chunks tool |
| `apps/backend/adk/quiz_agent.py` | Quiz BaseAgent wrapper calling generate_mcq_quiz tool |
| `apps/backend/adk/evaluator_agent.py` | Evaluator BaseAgent with dual mode: review (quality gating) and evaluate (student grading) |
| `apps/backend/adk/curriculum_tool.py` | ADK tool for vector retrieval using EmbeddingService + VectorStore |
| `apps/backend/adk/quiz_tool.py` | ADK tool wrapping QuizGeneratorAgent |
| `apps/backend/adk/evaluation_tool.py` | ADK tool wrapping TeacherReviewAgent.evaluate_answers |
| `conftest.py` | Root pytest conftest adding apps/backend to sys.path for adk.* imports |

---

## Files Modified

| File | Change |
|------|--------|
| `apps/backend/app/agents/orchestrator.py` | Refactored process_request to use ADK Runner + InMemorySessionService pipeline |
| `apps/backend/requirements.txt` | Updated google-adk==1.4.2, added google-genai>=1.0.0 |
| `pyproject.toml` | Added [tool.pytest.ini_options] with pythonpath = ['apps/backend'] |

---

## Files Deleted

None - all existing service and agent files preserved.

---

## Agent Hierarchy

RootAgent (root_agent.py)
  - PromptGuard (security gate - blocks injections)
  - RAGAgent (retrieves pgvector chunks)
  - PhysicsAgent (-> PhysicsSMEAgent.generate_response)
  - ChemistryAgent (-> ChemistrySMEAgent.generate_response)
  - QuizAgent (-> QuizGeneratorAgent.generate_quiz)
  - EvaluatorAgent
      - mode=review -> TeacherReviewAgent.review_response
      - mode=evaluate -> TeacherReviewAgent.evaluate_answers

---

## Intent Routing Logic (Root Agent)

| Intent | Path |
|--------|------|
| quiz_generation | RAG -> QuizAgent -> EvaluatorAgent (review) |
| answer_evaluation | EvaluatorAgent (evaluate) |
| doubt_solving / lesson_explanation / exam_preparation (Physics) | RAG -> PhysicsAgent [-> EvaluatorAgent if exam/intent/low-confidence] |
| doubt_solving / lesson_explanation / exam_preparation (Chemistry) | RAG -> ChemistryAgent [-> EvaluatorAgent if exam/intent/low-confidence] |
| Blocked (prompt injection) | PromptGuard -> blocked response |

---

## Evaluator Gating Rules

The EvaluatorAgent (Teacher Review) is conditionally triggered:
1. Always on quiz generation (quality review)
2. Always on NEET/KCET exam queries (exam alignment check)
3. Always on lesson_summary or quick_notes intents
4. Conditionally when routing confidence drops below 0.85

---

## Architectural Decisions

ADR-001: BaseAgent over LlmAgent
Using BaseAgent with custom _run_async_impl rather than ADKs LlmAgent because:
- SME agents call VertexAIService directly (controlled cost, no LLM routing overhead)
- Deterministic routing avoids unpredictable LLM-based sub-agent selection
- Pytest mocks target underlying service methods, preserved

ADR-002: Session State for Inter-Agent Communication
ADK InMemorySessionService with create_session(state=initial_state) ensures:
- Initial request metadata visible to all sub-agents at start
- State mutations within sub-agents persist via ctx.session.state
- No shared global state - each request gets an isolated session

ADR-003: Event Constructor (ADK 1.4.2)
Event schema in google-adk==1.4.2 extends LlmResponse with extra='forbid'.
Text output must be passed via:
  Event(author=self.name, content=types.Content(role='model', parts=[types.Part.from_text(text='...')]))
Not Event(author=..., output=...) as in older API samples.

ADR-004: No LLM Cost in Routing
All intent detection uses deterministic keyword matching - zero LLM tokens for routing.
Cost is only incurred during actual SME response generation and optional Teacher Review.

---

## API Contract Compatibility

The following API contracts are fully preserved - frontend requires no changes:

| Endpoint | Status |
|----------|--------|
| POST /api/v1/chat | Unchanged |
| POST /api/v1/quiz | Unchanged |
| POST /api/v1/evaluate | Unchanged |
| GET /api/v1/health | Unchanged |
| GET /api/v1/ready | Unchanged |

---

## MCP Future Migration Compatibility

The ADK tool functions (curriculum_tool.py, quiz_tool.py, evaluation_tool.py) are 
written as standalone async functions with optional tool_context: ToolContext parameters.
This design allows:
- Direct ADK tool registration today
- Future migration to MCP servers by wrapping these functions as MCP handlers
- No interface changes required in sub-agents

---

## Infrastructure Unchanged

| Component | Status |
|-----------|--------|
| Cloud Run (min=0, max=2) | Unchanged |
| Cloud SQL PostgreSQL + pgvector | Unchanged |
| Firebase Hosting (Next.js frontend) | Unchanged |
| Firestore session logging | Unchanged |
| Vertex AI Gemini Flash | Unchanged |
| Secret Manager | Unchanged |

---

Generated: Phase 1 ADK Migration - StudyMateAI MVP
