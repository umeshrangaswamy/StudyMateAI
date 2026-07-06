---
version: 1.1.0
last_updated: 2026-07-06
type: AntiGravity Prompt
phases: Phase 0 to Phase 9
description: Standardized prompt evolution roadmap for ADK, MCP, Skills migration, memory, CLI, and validation.
---

# StudyMateAI: Architecture Migration & Roadmap Prompts

This document outlines the master prompts and phase-by-phase execution instructions used to evolve StudyMateAI to its target multi-agent and tool-driven architecture.

---

## 🛠️ Master Migration Prompt

You are performing an architecture migration. Before creating files:

1. Analyze the entire repository.
2. Reuse existing files whenever possible.
3. Do not create duplicate architecture documents.
4. Update existing files instead of creating replacements when practical.
5. Remove obsolete files that conflict with the target architecture.
6. Generate a migration report listing:
   - Files created
   - Files modified
   - Files deleted
   - Architectural decisions made

### Reference Documentation
- [AGENTS.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/AGENTS.md)
- [specification.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/specification.md)

### Architectural Guardrails
Never introduce:
- GKE, ChromaDB, Pinecone, Redis, Apigee, or Cloud Armor (unless explicitly requested).

### Target Stack
- StudyMateAI MVP
- Google ADK
- Model Context Protocol (MCP)
- Agent Skills
- Vertex AI Gemini
- Cloud Run
- Cloud SQL + pgvector

---

## 🏁 Phase 0: Architecture Stabilization

### Goal
Create the architecture baseline required for all future phases.

### Prompt / Instructions
Execute Phase 0: Architecture Stabilization. Transform the current StudyMateAI repository into a Kaggle-ready MVP architecture baseline.

### Key Tasks
1. Scan the repository and identify duplicate or obsolete design documents.
2. Replace all occurrences of "Free Tier" with "MVP".
3. Create or update:
   - [specification.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/specification.md)
   - [architecture-vision.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/architecture-vision.md)
   - [kaggle-capstone-roadmap.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/kaggle-capstone-roadmap.md)
   - [kaggle-evaluation-mapping.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/kaggle-evaluation-mapping.md)
4. Upgrade Evaluator Agent design: Rename/refactor Evaluator to **Teacher Review Agent**.
5. Create Architecture Decision Records (ADRs):
   - `ADR-001-rag-strategy.md`
   - `ADR-002-agent-architecture.md`
   - `ADR-003-deployment-strategy.md`
   - `ADR-004-evaluator-strategy.md`
6. Update [README.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/README.md) and [AGENTS.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/AGENTS.md) to align with MVP terminology.
7. Remove obsolete architecture files.
8. Generate `docs/phase-0-migration-report.md` (detailing modified, deleted, created files and architecture summary).

*Constraint: Do not implement ADK or MCP yet.*

---

## 📦 Phase 1: ADK Migration

### Goal
Convert the custom agent layer into the Google ADK (Agent Development Kit) architecture.

### Prompt / Instructions
Execute Phase 1: Google ADK Migration.

### Key Tasks
1. Analyze current backend agent implementation.
2. Preserve existing business logic for Physics SME, Chemistry SME, RAG, Quiz, and Evaluator agents.
3. Introduce ADK architecture by creating `apps/backend/adk/`.
4. Create the ADK Root Agent to act as the primary orchestrator.
5. Migrate SME and utility agents to ADK sub-agents:
   - Physics Agent
   - Chemistry Agent
   - RAG Agent
   - Quiz Agent
   - Evaluator Agent
6. Remove legacy custom orchestration code that conflicts with ADK.
7. Preserve existing API contracts and keep frontend unchanged.
8. Generate `docs/phase-1-adk-migration-report.md`.

---

## 🧠 Phase 2: Skills Migration

### Goal
Formalize domain capabilities as explicit, testable agent skills.

### Prompt / Instructions
Execute Phase 2: Agent Skills Architecture.

### Key Tasks
1. Analyze existing ADK agents.
2. Extract agent capabilities into dedicated skill modules:
   - **Physics Agent Skills**: Explain Concept, Generate Summary, Generate Quick Notes, Prepare KCET, Prepare NEET, Generate Formula Sheet.
   - **Chemistry Agent Skills**: Explain Concept, Generate Summary, Generate Quick Notes, Prepare KCET, Prepare NEET, Generate Equation Sheet.
   - **Evaluator Skills**: Evaluate Answer, Evaluate Quiz, Detect Weak Topics.
   - **RAG Skills**: Search Textbook, Search Notes, Search Exam Papers.
3. Remove duplicate capabilities from agent files once encapsulated in skills.
4. Generate `docs/phase-2-skills-migration-report.md`.

---

## 🌐 Phase 3: MCP Migration

### Goal
Integrate Model Context Protocol (MCP) to decouple resource retrieval and assessments.

### Prompt / Instructions
Execute Phase 3: MCP Integration.

### Key Tasks
1. Create the MCP layer.
2. Implement two standalone MCP Servers:
   - **Knowledge MCP Server**
   - **Assessment MCP Server**
3. Expose the following MCP Tools:
   - **Knowledge Tools**: `search_curriculum`, `get_notes`, `get_formula_sheet`, `get_previous_questions`
   - **Assessment Tools**: `generate_quiz`, `evaluate_answer`, `recommend_revision`
4. Refactor ADK agents to consume MCP tools instead of direct database/utility calls.
5. Generate `docs/phase-3-mcp-migration-report.md`.

---

## 👩‍🏫 Phase 4: Teacher Review Evaluator

### Goal
Refactor evaluator logic to support a full validation loop via the Teacher Review Agent.

### Prompt / Instructions
Execute Phase 4: Teacher Review Evaluator.

### Key Tasks
1. Refactor Evaluator into a **Teacher Review Agent**.
2. Add validations for:
   - Academic Validation
   - Exam Alignment Validation
   - Response Quality Validation
   - Safety & Guardrail Validation
   - Student Assessment
3. Update routing so that Quiz Generation and Evaluation workflows must undergo mandatory validation.
4. Generate `docs/phase-4-evaluator-migration-report.md`.

---

## 💾 Phase 5: Learning Memory

### Goal
Create Firestore-backed persistent student memory profiles.

### Prompt / Instructions
Execute Phase 5: Learning Memory.

### Key Tasks
1. Implement Firestore connections to store student learning state.
2. Track: Quiz Scores, Weak Topics, Revision History, and Exam Goals.
3. Create Memory Services and a Progress Skill.
4. Generate `docs/phase-5-memory-migration-report.md`.

---

## 💻 Phase 6: Agent CLI

### Goal
Provide a unified CLI interface for managing tasks, questions, and revision planning.

### Prompt / Instructions
Execute Phase 6: Agent CLI.

### Key Tasks
1. Create the `studymate` CLI utility.
2. Implement commands:
   - `studymate ask`
   - `studymate quiz`
   - `studymate evaluate`
   - `studymate progress`
   - `studymate ingest`
3. Generate CLI documentation, usage examples, and test coverage.
4. Generate `docs/phase-6-cli-migration-report.md`.

---

## 🚀 Phase 7: Deployability Showcase

### Goal
Standardize infrastructure, build configurations, and deploy guide for GCP.

### Prompt / Instructions
Execute Phase 7: Deployability Showcase.

### Key Tasks
1. Standardize deployment configurations for Cloud Run and Firebase Hosting.
2. Implement Terraform configurations and GitHub Actions workflows.
3. Clean up obsolete deployment scripts.
4. Create a deployment architecture diagram, deployment guide, and reproducible setup guide.
5. Generate `docs/phase-7-deployability-report.md`.

---

## 📖 Phase 8: Antigravity Showcase

### Goal
Document the evolution story and provide architectural evolution overviews.

### Prompt / Instructions
Execute Phase 8: Antigravity Showcase.

### Key Tasks
1. Create `docs/antigravity-build-story.md` illustrating:
   - Monolithic to Multi-Agent Evolution
   - ADK and MCP generation details
   - Skill implementation details
2. Setup placeholders and paths for UI screenshots.
3. Generate `docs/phase-8-antigravity-report.md`.

---

## 🏆 Phase 9: Educational WOW Features

### Goal
Implement high-value academic tools to maximize classroom utility and learning outcomes.

### Prompt / Instructions
Execute Phase 9: Educational WOW Features.

### Key Tasks
1. Implement:
   - Exam Coach (interactive hint-giver)
   - Weak Topic Detector
   - Formula/Equation Sheet Generator
   - Personalized Revision Planner
   - Exam Readiness Score
2. Reuse existing agents and skills without introducing redundant agent services.
3. Generate `docs/phase-9-wow-features-report.md`.
