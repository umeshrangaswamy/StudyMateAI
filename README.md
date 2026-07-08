# StudyMateAI – MVP
This project has been developed using Vibe Coding with a spec‑driven architecture, leveraging the Antigravity IDE, and accomplished entirely with zero manual coding.  
The Antigravity platform was used for the complete end‑to‑end development process — extending the specification document, implementing development, managing cloud deployment, and conducting testing. This entire journey was achieved seamlessly through **Antigravity prompts**, without any manual coding.

StudyMateAI is an AI-powered academic mentor platform designed to assist students with curriculum-aligned learning support. It serves as an interactive teacher by explaining concepts, solving doubts, generating summaries/notes, generating quizzes, and evaluating answers within a controlled academic scope.

This repository implements the **MVP / Starter** architecture using a modular multi-agent system powered by the **Google Agent Development Kit (ADK)** and serverless Google Cloud Platform (GCP) resources.

# Application Link : https://project-2e926853-25a4-402b-a73.web.app/

## 📋 Table of Contents
- [Project Architecture](#project-architecture)
- [Multi-Agent Design](#multi-agent-design)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Academic Scope Boundaries](#academic-scope-boundaries)
- [Unified CLI Reference](#unified-cli-reference)
- [Development Setup](#development-setup)

---

## 🏗️ Project Architecture

```
                 +-----------------------+
                 |  Next.js Static UI   |
                 |   (Firebase Hosting)  |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |    FastAPI Backend    |
                 |      (Cloud Run)      |
                 +----+--------+------+--+
                       |        |      |
         +------------+        |      +-------------+
         |                     v                    |
+--------+--------+   +--------+--------+   +-------+-------+
|    Vertex AI    |   |    Cloud SQL    |   |   Firestore   |
| (Gemini/Embed)  |   | (Postgres+vector|   |  (Metadata/   |
+-----------------+   +-----------------+   |   Sessions)   |
                                            +---------------+
```

---

## 🤖 Multi-Agent Design

The application utilizes a modular orchestration architecture implemented via the **Google Agent Development Kit (ADK)**:

1. **`root_agent`** ([root_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/root_agent.py)): The entry point and workflow orchestrator. Performs security checks via `PromptGuard`, detects intent and target entrance exams (KCET/NEET), and dynamically routes queries to sub-agents.
2. **`rag_agent`** ([rag_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/rag_agent.py)): Fetches relevant textbooks/notes context from Cloud SQL using `pgvector` similarity search, constrained by active metadata filters (subject, year, board).
3. **`physics_agent`** ([physics_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/physics_agent.py)): Solves student doubts, details explanations, and generates customized Physics formula sheets using domain-specific skills.
4. **`chemistry_agent`** ([chemistry_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/chemistry_agent.py)): Answers queries and formats equation/reaction sheets using domain-specific skills.
5. **`quiz_agent`** ([quiz_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/quiz_agent.py)): Generates syllabus-aligned multiple choice question (MCQ) sets based on retrieved context.
6. **`evaluator_agent`** ([evaluator_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/evaluator_agent.py)): Handles mandatory quality verification (Teacher Review) for generated material and grades student-submitted answers against ground-truth keys.

---

## 📂 Repository Structure

The project is organized as a monorepo:

```
StudyMateAI/
├── apps/
│   ├── backend/            # FastAPI application & Google ADK Agents (Cloud Run)
│   │   ├── adk/            # Google ADK agent implementations and skills
│   │   │   └── skills/     # Domain-specific pedagogical skills (Physics, Chemistry, RAG, Evaluator)
│   │   ├── app/            # Legacy backend logic, core endpoints, services, security
│   │   └── cli.py          # Unified developer command-line interface
│   └── frontend/           # Next.js static site, Tailwind CSS, Inter font (Firebase Hosting)
├── docs/                   # Architectural specification volumes 1-4 and reports
├── infra/                  # GCP Infrastructure configs (Terraform & gcloud scripts)
├── packages/
│   ├── prompts/            # System prompt configurations, markdown-based templates
│   └── shared/             # Shared Python schema models (Pydantic) & Firestore utilities
├── scripts/
│   └── ingestion/          # Document processing, chunking & vector embedding ingestion
└── tests/                  # Backend unit and integration tests (pytest)
```

---

## 🛠️ Technology Stack

- **Frontend:** Next.js (Static HTML Export), TypeScript, Tailwind CSS, hosted on Firebase Hosting.
- **Backend:** FastAPI (Python 3.11) containerized on Cloud Run (min instances = 0, max = 2).
- **LLM & Embeddings:** Vertex AI Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`), Vertex AI Text Embeddings (`text-embedding-004`).
- **Vector Database:** Cloud SQL PostgreSQL with the `pgvector` extension.
- **Metadata Store:** Cloud Firestore (manages student progress metrics & transaction history).
- **File Storage:** Google Cloud Storage (GCS) containing raw syllabus textbooks.

---

## 🎓 Academic Scope & Constraints

As per the **MVP Rules**:
- **Subjects Implemented:** Physics and Chemistry only.
- **Entrance Exams Implemented:** KCET and NEET only.
- **Design Only (Deferred for Future):** Mathematics, Biology, English, JEE.
- **Response Style:** Simple, crisp, teacher-like, exam-focused.
- **RAG constraint:** Always apply metadata filters before performing similarity searches to optimize cost and retrieval quality.

---

## 💻 Unified CLI Reference

A comprehensive developer command-line utility is available inside the backend directory:

```bash
# Navigate to backend
cd apps/backend

# Ask a conceptual doubt
python cli.py ask "Explain Newton's third law of motion" --subject physics

# Generate an MCQ quiz
python cli.py quiz --subject chemistry --board "Karnataka State Board" --year "2nd PUC"

# Evaluate student answers (expects questions JSON and answers JSON)
python cli.py evaluate '[{"id": 1, "question": "...", "correct_option": "A"}]' '{"1": "A"}'

# Fetch student learning progress report
python cli.py progress --user_id "default_student"

# Ingest curriculum textbook file
python cli.py ingest "path/to/textbook.txt" --subject physics
```

---

## 🚀 Development Setup

### 🔐 Prerequisites
Before running the deployment script, make sure you are authenticated with both Google Cloud and Firebase:
1. **Google Cloud SDK (gcloud CLI)**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
2. **Firebase CLI**:
   ```bash
   npx firebase login
   ```

### 🚢 Unified One-Click Deployment
To deploy the entire stack (both the FastAPI Backend to Cloud Run and the Next.js static site to Firebase Hosting), execute the unified deployment script in the project root:
```bash
./deploy.sh
```

### 💻 Running Locally
For running the services individually in a development environment:
* **FastAPI Backend**: Refer to the [Backend Setup Guide](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/README.md)
* **Next.js Frontend**: Refer to the [Frontend Setup Guide](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/frontend/README.md)
