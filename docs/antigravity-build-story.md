# StudyMateAI: Antigravity Build Story

This document showcases how the Antigravity developer agent built and evolved the StudyMateAI MVP.

---

## 1. Architecture Evolution
StudyMateAI evolved from a monolithic backend design into a standardized multi-agent architecture utilizing state-of-the-art tools:

```
+-------------------------------------------------------------+
| Phase 0: Monolithic Router                                  |
|   Single process, direct API calls, manual validation       |
+------------------------------o------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| Phase 1: Google ADK Migration                               |
|   RootAgent coordinating ADK sub-agents in session runners  |
+------------------------------o------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| Phase 2-3: Agent Skills + MCP integration                  |
|   Granular domain functions, FastMCP tool servers           |
+------------------------------o------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| Phase 4-6: Gated Quality, Memory & CLI                      |
|   Safety reviews, Firestore profiles, studymate terminal    |
+-------------------------------------------------------------+
```

---

## 2. ADK, MCP & Skill Generation

### Skill Generation
Domain capabilities were isolated into simple, testable python functions within the `adk/skills/` package. This decoupling allowed:
*   Clear parameter tracking without state contamination.
*   Direct mapping to API tools.

### MCP Generation
MCP tools (`search_curriculum`, `get_notes`, `generate_quiz`, `evaluate_answer`, etc.) were created as standard functions decorated by the `FastMCP` framework. To allow optimal performance and skip process instantiation during test suites, the `mcp_server/client.py` was refactored to execute the underlying python functions directly in-process.

---

## 3. Screenshots Placeholder Structure
To document the running application visually, placeholders for showcase images are structured under `docs/screenshots/`:
*   `docs/screenshots/01-doubt-solving-response.png`: Showing Physics concept explanation with textbook source citations.
*   `docs/screenshots/02-quiz-generation-view.png`: Showing the 5-MCQ interactive exam generator output.
*   `docs/screenshots/03-evaluation-grades-feedback.png`: Showing student answer checking and teacher review approval logs.
*   `docs/screenshots/04-progress-profile.png`: Terminal dashboard showing cumulative weak topics and quiz scores.
