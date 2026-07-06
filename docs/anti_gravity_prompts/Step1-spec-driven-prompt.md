---
version: 1.0.0
last_updated: 2026-07-06
type: AntiGravity Prompt
phase: Phase 0 (Baseline Setup)
description: Specification-driven prompt for scaffolding the initial StudyMateAI MVP.
---

# StudyMateAI: Initial Spec-Driven Scaffolding Prompt

You are Antigravity, an agentic software engineer. Your task is to scaffold and implement the initial StudyMateAI MVP based on the provided specifications.

## 📋 Objective
Build a curriculum-grounded, multi-agent academic mentor platform for Class 12 / 2nd PUC Physics and Chemistry, supporting KCET/NEET exam preparation, doubt solving, and automatic grading.

## 📖 Reference Architecture Documents
- [volume-1-product-architecture.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/volume-1-product-architecture.md)
- [volume-2-agent-architecture.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/volume-2-agent-architecture.md)
- [volume-3-gcp-architecture.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/volume-3-gcp-architecture.md)
- [volume-4-data-rag-architecture.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/docs/volume-4-data-rag-architecture.md)

## 🛠️ Tasks & Scope

### 1. Project Scaffolding
- Initialize the monorepo structure.
- Define `apps/backend` (FastAPI) and `apps/frontend` (Next.js/TypeScript/Tailwind CSS).
- Setup the core configuration, environment variables, and Docker files.

### 2. Backend Implementation (FastAPI)
- **Security**: Implement `PromptGuard` in `apps/backend/app/security/prompt_guard.py` to block prompt injections.
- **Orchestrator Agent**: Implement `orchestrator.py` to route queries, detect intents (doubt-solving, quiz generation, answer evaluation), and log sessions to Firestore.
- **SME Agents**: Implement Physics and Chemistry SME Agents to formulate responses based on RAG context.
- **RAG Agent**: Retrieve textbook segments and exam papers from Cloud SQL PostgreSQL using pgvector embeddings.
- **Quiz Generator Agent**: Create 5 MCQ quizzes mapped to the selected curriculum.
- **Evaluator Agent**: Implement scoring, grade responses, and suggest revision tips.

### 3. Frontend Implementation (Next.js)
- Build a premium, responsive student dashboard.
- Create views for conceptual doubt solving, quiz generation, and evaluation feedback.
- Integrate routing and layout matching the design specifications.

### 4. Database & Services
- Set up Firestore logging services.
- Establish connections for Vertex AI Gemini Flash and Vertex AI Embeddings.
- Configure PostgreSQL database connectivity with pgvector search capabilities.

## ⚠️ Guardrails & Constraints
- Stay strictly within the scope (0-10 users, Physics/Chemistry, KCET/NEET).
- Do not implement GKE, Redis, Apigee, Cloud Armor, Pinecone, or ChromaDB.
- Keep answers crisp, teacher-like, and exam-focused.
