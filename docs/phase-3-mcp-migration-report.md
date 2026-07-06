# Phase 3: MCP Integration Report

## MCP Architecture
Phase 3 establishes a Model Context Protocol (MCP) layer using in-process standard protocol tooling (`FastMCP` from the `mcp` SDK). This design ensures zero additional operational overhead (keeping min-instances=0, max-instances=2 in Cloud Run) while formally standardising tool invocation boundaries for both current and future agent systems.

To avoid name-shadowing conflicts with the official third-party `mcp` Python SDK library, the local integration module is placed under `mcp_server/`.

```
       +---------------------------------------------+
       |             RootAgent / Orchestrator        |
       +----------------------o----------------------+
                              |
                              v
       +---------------------------------------------+
       |       MCP Client (mcp_server.client)        |
       +-------o-----------------------------o-------+
               |                             |
               v                             v
+-----------------------------+ +-----------------------------+
|    Knowledge MCP Server     | |   Assessment MCP Server     |
+-----------------------------+ +-----------------------------+
| - search_curriculum         | | - generate_quiz             |
| - get_notes                 | | - evaluate_answer           |
| - get_formula_sheet         | | - recommend_revision        |
| - get_previous_questions    | |                             |
+--------------o--------------+ +--------------o--------------+
               |                             |
               +--------------o--------------+
                              |
                              v
               +-----------------------------+
               |     Domain Skills Layer     |
               +-----------------------------+
```

---

## Tool Catalog

### 1. Knowledge MCP Server (`mcp_server/knowledge_server.py`)
Exposes curriculum contexts and syllabus guidelines:
*   `search_curriculum`: Fetches general textbook curriculum chunks grounded in subject/board/year/chapter/exam filters.
*   `get_notes`: Retrieves notes/summary-oriented curriculum chunks.
*   `get_formula_sheet`: Generates standard Physics formula or Chemistry equation sheets.
*   `get_previous_questions`: Retrieves curriculum chunks specifically tagged with KCET/NEET exam metadata.

### 2. Assessment MCP Server (`mcp_server/assessment_server.py`)
Exposes testing and evaluation utilities:
*   `generate_quiz`: Generates a structured MCQ quiz (5 questions, 4 options, answer keys, explanations).
*   `evaluate_answer`: Grades student MCQ/subjective submissions.
*   `recommend_revision`: Identifies weak topics based on assessment results and recommends focused study modules.

---

## Removed & Modified Code
*   **Removed**: Redundant imports of direct evaluation wrappers (`evaluate_student_answers`, `generate_mcq_quiz`, `retrieve_curriculum_chunks`) inside ADK agent controllers (`rag_agent.py`, `quiz_agent.py`, `evaluator_agent.py`).
*   **Modified**: ADK agent controllers updated to route through `mcp_server.client.call_tool` instead of calling service objects or skill modules directly.

---

## Migration Impact & Shadowing Mitigation
*   **Module Conflict Resolution**: Renamed the local MCP server directory from `mcp/` to `mcp_server/` to prevent Python from shadowing the third-party `mcp` library from PyPI.
*   **Clean Boundaries**: The system separates business logic (in service layers and SME classes) from protocol concerns.
*   **No Deployment Overhead**: In-process stdio/direct mapping is used instead of exposing network ports, retaining low-cost MVP parameters.
*   **Extensibility**: The catalog complies with Model Context Protocol specifications, making it ready to be exposed to external agents/IDE clients immediately.
