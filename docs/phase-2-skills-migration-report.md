# Phase 2: Agent Skills Migration Report

## Overview
Phase 2 introduces an explicit skills layer to separate agent capabilities from the routing and session orchestration logic. By extracting the core pedagogical behaviors into standalone, reusable functions within `apps/backend/adk/skills/`, we improve modularity, simplify individual agent files, and set up a clean path for MCP tool exposure in Phase 3.

---

## Files Created

| File | Purpose |
|------|---------|
| [adk/skills/__init__.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/__init__.py) | Package entry point exporting all skill functions across domains. |
| [adk/skills/physics_skills.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/physics_skills.py) | Standalone Physics skill functions (`explain_concept`, `generate_summary`, `generate_quick_notes`, `prepare_kcet`, `prepare_neet`, `generate_formula_sheet`). |
| [adk/skills/chemistry_skills.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/chemistry_skills.py) | Standalone Chemistry skill functions (`explain_concept`, `generate_summary`, `generate_quick_notes`, `prepare_kcet`, `prepare_neet`, `generate_equation_sheet`). |
| [adk/skills/evaluator_skills.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/evaluator_skills.py) | Standalone Evaluator skill functions (`evaluate_answer`, `evaluate_quiz`, `detect_weak_topics`). |
| [adk/skills/rag_skills.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/rag_skills.py) | Standalone RAG retrieval skill functions (`search_textbook`, `search_notes`, `search_exam_papers`). |

---

## Files Modified

| File | Change |
|------|--------|
| [adk/physics_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/physics_agent.py) | Refactored `PhysicsAgent` to dispatch requests to the new explicit physics skills rather than calling monolithic `PhysicsSMEAgent.generate_response`. |
| [adk/chemistry_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/chemistry_agent.py) | Refactored `ChemistryAgent` to dispatch to the chemistry skills. |
| [adk/evaluator_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/evaluator_agent.py) | Refactored `EvaluatorAgent` to leverage the evaluator skills (`evaluate_answer`, `evaluate_quiz`, `detect_weak_topics`). |
| [adk/rag_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/rag_agent.py) | Refactored `RAGAgent` to select from specific RAG skills based on intent and exam context. |

---

## Files Deleted
None. Existing components were preserved and wrapped with clean skill interfaces.

---

## Architectural Decisions

### 1. Skill Granularity
Rather than having a single `generate_response` endpoint with varying prompt parameters, we split the logic into explicit functions reflecting pedagogical tasks (e.g. `generate_formula_sheet`, `detect_weak_topics`). This enhances traceability and logs, and maps perfectly to future MCP tools.

### 2. Retention of Custom SME/Evaluator/RAG Classes
The underlying agent execution classes (`PhysicsSMEAgent`, `ChemistrySMEAgent`, `TeacherReviewAgent`, `RAGAgent`) are kept intact in `apps/backend/app/agents/` as the functional engine. The skill layer acts as a clean function-based boundary wrapping these classes.

### 3. Graceful Fallbacks in RAG Retrieval
If a specific retrieval skill fails (e.g. `search_exam_papers` being called without a valid entrance exam context), the ADK agent handles the exception and falls back to general `search_textbook` retrieval, keeping system execution robust.
