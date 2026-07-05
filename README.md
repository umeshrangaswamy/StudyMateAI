# StudyMateAI – Free Tier

StudyMateAI is an AI-powered academic mentor platform designed to assist students with curriculum-aligned learning support. It serves as an interactive teacher by explaining concepts, solving doubts, generating summaries/notes, generating quizzes, and evaluating answers within a controlled academic scope.

This repository implements the **Free Tier / Starter** architecture using serverless and low-cost Google Cloud Platform (GCP) resources.

## 📋 Table of Contents
- [Project Architecture](#project-architecture)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Academic Scope Boundaries](#academic-scope-boundaries)
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

The system uses a multi-agent pattern following the sequence:
`Understand (Orchestrator) -> Retrieve (RAG) -> Reason/Generate (Physics/Chemistry SME) -> Evaluate (Evaluator) -> Respond`

---

## 📂 Repository Structure

The project is organized as a monorepo structure:

```
studymateai/
├── .github/
│   └── workflows/          # CI/CD deployment files
├── apps/
│   ├── backend/            # FastAPI application (Cloud Run)
│   └── frontend/           # Next.js static site (Firebase Hosting)
├── docs/                   # Architectural specification volumes 1-4
├── infra/
│   ├── gcloud/             # GCP environment helper scripts
│   └── terraform/          # IaC templates for database, storage, and run setup
├── packages/
│   ├── prompts/            # Reusable AI prompt assets
│   └── shared/             # Shared Python schema models & utilities
├── scripts/
│   └── ingestion/          # Document processing & ingestion pipeline scripts
└── tests/                  # Backend unit and integration tests
```

---

## 🛠️ Technology Stack

- **Frontend:** Next.js (Static HTML Export), TypeScript, Tailwind CSS, hosted on Firebase Hosting.
- **Backend:** FastAPI (Python 3.11) containerized on Cloud Run (min instances = 0, max = 2).
- **LLM/Embeddings:** Vertex AI Gemini Flash (`gemini-1.5-flash`), Vertex AI Text Embeddings (`text-embedding-004`).
- **Vector Database:** Cloud SQL PostgreSQL with the `pgvector` extension.
- **Metadata Store:** Cloud Firestore.
- **File Storage:** Google Cloud Storage (GCS).

---

## 🎓 Academic Scope & Constraints

As per the **Free Tier Rules**:
- **Subjects Implemented:** Physics and Chemistry only.
- **Entrance Exams Implemented:** KCET and NEET only.
- **Design Only (Deferred for Future):** Mathematics, Biology, English, JEE.
- **Response Style:** Simple, crisp, teacher-like, exam-focused.
- **RAG constraint:** Always apply metadata filters before performing similarity searches to optimize cost and retrieval quality.

---

## 🚀 Development Setup

For setup and installation guidelines, please refer to:
- Backend setup: [apps/backend/README.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/README.md)
- Frontend setup: [apps/frontend/README.md](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/frontend/README.md)
