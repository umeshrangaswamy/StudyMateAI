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

### Detailed Agent Architecture

```mermaid
graph TD
    %% Client Tier
    subgraph ClientTier ["Client Tier"]
        Browser["Web Browser"]
    end

    %% Ingress Tier
    subgraph IngressTier ["Entry / Ingress Tier"]
        Firebase["Firebase Hosting CDN<br/>(Static UI Assets)"]
        LoadBalancer["GCP Load Balancer / Routing"]
    end

    %% Backend Container Tier (Cloud Run)
    subgraph BackendTier ["Backend Container Tier (Cloud Run)"]
        FastAPI["FastAPI (study-buddy-api)"]
        Orchestrator["Orchestrator Agent"]
        RAGAgent["RAG Retrieval Agent"]
        PhysicsSME["Physics SME Agent"]
        ChemistrySME["Chemistry SME Agent"]
        QuizGen["Quiz Generator Agent"]
        Evaluator["Evaluator Agent"]
    end

    %% Data & Vector Store Tier
    subgraph DataStoreTier ["Data & Vector Store Tier"]
        CloudSQL["Cloud SQL PostgreSQL"]
        pgvectorIndex["pgvector index/lookup"]
        pgvectorExt["pgvector Extension"]
        Firestore["Firestore DB"]
        CloudStorage["Cloud Storage Bucket"]
        
        CloudSQL --> pgvectorIndex --> pgvectorExt
    end

    %% Cognitive Tier
    subgraph CognitiveTier ["Cognitive Tier - Vertex AI"]
        Gemini["Gemini 2.5 Flash / Lite Model"]
        Embeddings["text-embedding-004 Model"]
    end

    %% Interactions
    Browser -->|1. Downloads UI Assets| Firebase
    Browser -->|2. POST /api/ask| LoadBalancer
    LoadBalancer -->|3. Routes Request| FastAPI
    FastAPI -->|4. Triggers process_request| Orchestrator
    
    %% RAG flow
    Orchestrator -->|5. Search query/Get retrieved context| RAGAgent
    RAGAgent -->|5a. Similarity cosine search| CloudSQL
    RAGAgent -->|5b. Embed text query| Embeddings
    
    %% SME flow
    Orchestrator -->|6. Route query + RAG Context| PhysicsSME
    PhysicsSME -->|6a. Generate detailed explanation| Gemini
    
    Orchestrator -->|7. Route query + RAG Context| ChemistrySME
    ChemistrySME -->|7a. Generate detailed explanation| Gemini
    
    %% Quiz flow
    Orchestrator -->|8. Trigger Quiz Setup| QuizGen
    QuizGen -->|8a. Construct structured JSON| Gemini
    
    %% Evaluator flow
    Orchestrator -->|9. Trigger Evaluation| Evaluator
    Evaluator -->|9a. Evaluate response format/target| Gemini
    
    %% Validation loops
    PhysicsSME -->|10. Validate Output completeness| Evaluator
    ChemistrySME -->|10. Validate Output completeness| Evaluator
    Evaluator -->|11. Return review decision| Orchestrator
    
    %% Return response
    Orchestrator -->|12. Send approved answer + Quiz JSON| FastAPI
    FastAPI -->|13. Return JSON payload| Browser
    
    %% Auxiliary logging & ingestion
    FastAPI -.->|14. Async log transactions| Firestore
    FastAPI -.->|15. Ingest Textbook PDFs| CloudStorage

    %% Styling with high-contrast text color for both light/dark markdown viewers
    style Browser fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    style Firebase fill:#faf5ff,stroke:#7e22ce,stroke-width:2px,color:#581c87;
    style LoadBalancer fill:#faf5ff,stroke:#7e22ce,stroke-width:2px,color:#581c87;
    style FastAPI fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style Orchestrator fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style RAGAgent fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style PhysicsSME fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style ChemistrySME fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style QuizGen fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style Evaluator fill:#f0fdf4,stroke:#15803d,stroke-width:2px,color:#14532d;
    style CloudSQL fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    style pgvectorIndex fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    style pgvectorExt fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    style Firestore fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    style CloudStorage fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12;
    style Gemini fill:#fff1f2,stroke:#be123c,stroke-width:2px,color:#881337;
    style Embeddings fill:#fff1f2,stroke:#be123c,stroke-width:2px,color:#881337;
```

---

## 🤖 Multi-Agent Design

The application utilizes a modular orchestration architecture implemented via the **Google Agent Development Kit (ADK)** and the **Model Context Protocol (MCP)**:

1. **`root_agent`** ([root_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/root_agent.py)): The workflow coordinator and gateway. Performs security checks via `PromptGuard`, routes requests dynamically based on detected intent, and manages session state.
2. **`rag_agent`** ([rag_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/rag_agent.py)): A context retrieval coordinator that communicates with the database layer using embeddings to fetch curriculum notes.
3. **`physics_agent`** ([physics_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/physics_agent.py)): Dispatches Physics concept explanations, quick study notes, and formula sheets.
4. **`chemistry_agent`** ([chemistry_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/chemistry_agent.py)): Handles Chemistry explanations, reactions, mechanisms, and chemical equation sheets.
5. **`quiz_agent`** ([quiz_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/quiz_agent.py)): Interacts with the MCP Assessment Server to generate structured multiple-choice quizzes.
6. **`evaluator_agent`** ([evaluator_agent.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/evaluator_agent.py)): Performs Teacher Review validation (factual correctness and completeness) and grades student quiz submissions.

---

## 📂 Repository Structure

The project is organized as a monorepo with dedicated microservices and shared packages:

```
StudyMateAI/
├── apps/
│   ├── backend/                # FastAPI Application & Cloud Run Configs
│   │   ├── adk/                # Google ADK agent wrappers and named skills
│   │   │   ├── skills/         # Individual agent skill handlers (Physics, Chemistry, RAG, Evaluator)
│   │   │   │   ├── chemistry_skills.py  # Named skills for Chemistry (concept, summary, notes, kcet, neet, reactions)
│   │   │   │   ├── physics_skills.py    # Named skills for Physics (concept, summary, notes, kcet, neet, formulas)
│   │   │   │   ├── progress_skill.py    # Helper utility for tracking student progress metrics in Firestore
│   │   │   │   └── rag_skills.py        # Vector search retrieval skills
│   │   │   ├── chemistry_agent.py  # Wrapper agent class for Chemistry domain routing
│   │   │   ├── physics_agent.py    # Wrapper agent class for Physics domain routing
│   │   │   ├── quiz_agent.py       # Wrapper agent class that delegates quiz building
│   │   │   ├── quiz_tool.py        # Helper utility for calling MCQ generation tools
│   │   │   └── root_agent.py       # Base workflow routing coordinator and security checker
│   │   ├── app/                # Main application core
│   │   │   ├── agents/         # SME concrete agents executing text-generation calls (physics_sme.py, chemistry_sme.py)
│   │   │   ├── api/            # API Router and REST endpoints (endpoints.py)
│   │   │   ├── core/           # Configuration management (config.py) and logging definitions
│   │   │   ├── models/         # Pydantic JSON request (request_models.py) and response schemas
│   │   │   ├── security/       # Input validation guardrails (prompt_guard.py - checks for SQL injection & prompt overrides)
│   │   │   └── services/       # Vertex AI SDK wrappers, pgvector vector store and Firestore connectors
│   │   ├── mcp_server/         # FastMCP Server implementations
│   │   │   ├── assessment_server.py # FastMCP tools for generating quizzes and grading answers
│   │   │   ├── client.py       # Client routing utility for invoking MCP server tools
│   │   │   └── knowledge_server.py  # FastMCP tools for similarity searches and formula fetching
│   │   ├── cli.py              # CLI management tool for backend developer commands
│   │   ├── Dockerfile          # Multi-stage container definition for Cloud Run deployment
│   │   └── requirements.txt    # Backend Python dependencies
│   └── frontend/               # Next.js Static Web Application (Firebase Hosting)
│       ├── src/app/            # Main React components, landing pages (page.tsx) and styling
│       └── tailwind.config.js  # Styling guidelines configuration file
├── docs/                       # Specifications & Architectural volumes
│   ├── anti_gravity_prompts/   # Step-by-step vibe coding spec prompts for Antigravity IDE
│   │   └── Step1-spec-driven-prompt.md # Initial repository and skeleton setup instructions
│   ├── volume-1-product-architecture.md # Product goals, user flow, MVP scopes (Physics, Chemistry, NEET, KCET)
│   ├── volume-2-agent-architecture.md   # ADK orchestration workflow, SME design, session details
│   ├── volume-3-gcp-architecture.md     # Serverless Cloud Run deployment, GCS, Firestore setups
│   ├── volume-4-data-rag-architecture.md # RAG chunking layout, metadata schema, vector search details
│   └── specification.md        # Technical specifications and functional boundaries for developers
├── packages/
│   ├── prompts/                # System instructions (physics_sme.md, chemistry_sme.md, global_system.md)
│   └── shared/                 # Common Python classes and database connectors
├── scripts/
│   └── ingestion/              # Ingest scripts for curriculum chunking and embedding
├── AGENTS.md                   # Global instruction rules and architecture boundaries for the AI Agents
├── deploy.ps1                  # Windows One-Click PowerShell Deployment Script
├── deploy.sh                   # Linux/Unix One-Click Bash Deployment Script
└── tests/                      # Pytest unit tests (test_endpoints.py, test_cli.py)
```

---

## 🛠️ Technology Stack

| Component / Tool | Purpose / Role | Key Details / Notes |
| :--- | :--- | :--- |
| **Next.js & React** | Client Interface UI | Configured with static export to minimize client-side CPU usage and hosting costs. |
| **FastAPI** | Backend Web API | High-performance Python async framework serving requests on Cloud Run. |
| **Google Agent Development Kit (ADK)** | Multi-Agent Orchestration | Standardizes session state propagation, tools calling, and prompt management. |
| **Model Context Protocol (MCP)** | Decoupled Tool Server | Provides modular tools (Assessment and Knowledge search) via FastMCP server wrapper. |
| **Tailwind CSS** | Styling System | Curated harmonious dark themes, outfits, and responsive grid layouts. |
| **Vertex AI Gemini 2.5 Flash / Lite** | LLM Engine | Generates concept explanations and structures JSON schema quizzes. |
| **Vertex AI text-embedding-004** | Vector Embeddings | Translates curriculum textbook text and user queries into 768-dimension vectors. |
| **Cloud SQL PostgreSQL & pgvector** | Vector DB | Stores and indexes curriculum textbook text chunks using cosine distance metrics. |
| **Cloud Firestore** | Progress Tracker & Logs | Manages transaction details, student progress scores, and session logs. |
| **Google Cloud Storage (GCS)** | Textbook Storage | Retains raw curriculum textbook files for processing and RAG pipeline ingestion. |
| **Firebase Hosting** | Static CDN | Globally cached deployment endpoint for front-end static files. |

---

## 🎯 MVP Implementation Scope

The current implementation (MVP) provides a lightweight, serverless framework focused on cost efficiency and immediate feedback loops for up to 10 active concurrent users:

* **Academic Coverage**: Physics and Chemistry subjects tailored to 2nd PUC (12th Grade) board standards.
* **Entrance Scope**: Targeted prep models for Karnataka Common Entrance Test (KCET) and National Eligibility cum Entrance Test (NEET).
* **Multi-Agent Orchestration**: Core agent workflows (`Root`, `RAG`, `Physics`, `Chemistry`, `Quiz`, `Evaluator`) managed via the Google ADK and FastMCP tool clients.
* **RAG Constraints**: Baseline similarity searches utilizing Cloud SQL Postgres with `pgvector` index lookups, constrained to a strict `top_k = 3` retrieval limits to prevent token overload.
* **Output Guidelines & Constraints**:
  - **Concise Response Style**: Word limit of **300 words** for topic explanations; quizzes generate exactly **5 questions**.
  - **Detailed Response Style**: No word limit; quizzes generate **10 to 20 questions**.
  - **Exam & Entrance Preparation Intents**: Automatically exempt from word-limit cutoffs to ensure full Q&A and MCQ generation.
  - **Doubt Solving Hook**: Explanations for non-exam prep intents append **exactly 3 Board Exam-style practice questions** and **exactly 3 Entrance Exam-style practice questions** (without answers) plus a list of **Related Topics** for student self-study.
  - **Tutoring Explanation Response Structure**:
    1. **Definition**: Clear, one-line definition of the concept.
    2. **Explanation**: In-depth coverage (concise or detailed based on selected style).
    3. **Real-life Example**: A relatable, everyday application showing the concept in action.
    4. **Formula / Chemical Reaction**: Formatted using LaTeX block/inline equations (e.g. $$F = \frac{kq_1q_2}{r^2}$$ or $$2H_2 + O_2 \rightarrow 2H_2O$$).
    5. **KCET/NEET Tip**: Important values, exam traps, and high-yield focus areas.
    6. **Practice Questions & Related Topics**: As defined in the doubt solving hook.
  - **Chapter Summary Response Structure**:
    - **Chapter Overview**: 2-3 sentences general summary.
    - **Key Concepts & Definitions**: Bulleted list of core definitions.
    - **Important Laws, Formulas & Reactions**: Core laws/equations rendered in LaTeX.
    - **Summary of Key Subtopics**: Brief 1-2 sentence summaries of each sub-theme.
    - **KCET/NEET Focus Points**: Key exam strategies.
    - **Practice Questions & Related Topics**: Practice exercises and related study links.

---

## 🚀 Enterprise Production-Grade Target Scope

The target architecture (Enterprise Scale) is designed to scale horizontally to support thousands of concurrent students with high availability and low latency:

* **Academic Expansion**: Dedicated Subject Matter Experts (SMEs) for Mathematics, Biology, English, and other core curriculums.
* **Exam Coverage**: Full prep capabilities for Joint Entrance Examination (JEE) and major state/national board schemas (CBSE, ICSE, state boards).
* **Scale-Out Infrastructure**:
  - Migration of Cloud Run tasks to auto-scaling **Google Kubernetes Engine (GKE)** nodes.
  - Integration of **GCP Apigee** for advanced API routing, threat protection, and usage quota billing.
  - Placement of **Cloud Armor** WAF layers to safeguard against DDoS attacks.
* **High-Performance Data Tier**:
  - Upgrading the vector search to **Vertex AI Vector Search** or serverless **Pinecone / ChromaDB** to handle larger vector collections.
  - Setting up a **Redis Cache** layer to store frequently requested explanations, formulas, and quiz blocks to reduce model call costs.
  - Implementation of real-time streaming data ingestion pipelines utilizing Apache Kafka or GCP Pub/Sub for textbook notes updates.

---

## 💻 Unified CLI Reference

A comprehensive developer command-line utility is available inside the backend directory. Execute it to test core capabilities directly from your terminal:

```bash
# Navigate to backend directory
cd apps/backend

# 1. Ask a conceptual doubt (routes to relevant SME agent)
python cli.py ask "Explain Coulomb's Law" --subject physics --year "2nd PUC" --board "Karnataka State Board"

# 2. Generate an MCQ quiz (specifies target subject, grade level, and board)
python cli.py quiz --prompt "Chemical Bonding" --subject chemistry --year "2nd PUC" --board "Karnataka State Board"

# 3. Evaluate student answers (expects a JSON array of questions and key-value answers map)
python cli.py evaluate '[{"id":1,"question":"An ionic bond is formed by...","correct_option":"B"}]' '{"1":"B"}' --subject chemistry

# 4. Fetch student learning progress report
python cli.py progress --user_id "default_student"

# 5. Ingest curriculum textbook file
python cli.py ingest "path/to/notes.txt" --subject physics --board "Karnataka State Board"
```

---

## 🚀 Environment Setup & Deployment

### 💻 Windows Local Laptop Setup
Follow these steps to configure your local Windows machine with all required tools:
1. **Python 3.11/3.13**: Install Python from the official site and ensure it is added to your environment `PATH`.
2. **Node.js**: Install Node.js LTS (version 18+) to run the Next.js compilation step.
3. **Google Cloud SDK**:
   - Download and install the [Cloud SDK installer](https://cloud.google.com/sdk/docs/install-sdk#windows).
   - Authenticate with your GCP account:
     ```powershell
     gcloud auth login
     gcloud auth application-default login
     ```
4. **Firebase CLI**:
   - Install the Firebase CLI globally via npm:
     ```powershell
     npm install -g firebase-tools
     ```
   - Authenticate with your Firebase account:
     ```powershell
     firebase login
     ```

### 🚢 One-Click Cloud Deployment
Deploy the entire application (FastAPI backend container on Cloud Run and Next.js frontend on Firebase Hosting) using a single command:

* **On Windows (PowerShell)**:
  ```powershell
  powershell -File deploy.ps1
  ```
* **On macOS / Linux (Bash)**:
  ```bash
  chmod +x deploy.sh
  ./deploy.sh
  ```

### 💻 Running Locally
* **FastAPI Backend**: Refer to the [Backend Setup Guide](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/README.md)
* **Next.js Frontend**: Refer to the [Frontend Setup Guide](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/frontend/README.md)

---

## ⚙️ Configuration Reference (Environment Variables)

The backend behavior is governed by the following environment variables. In local development, these can be set in a `.env` file at `apps/backend/.env`.

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `GOOGLE_CLOUD_PROJECT` | `studymateai-dev` | Google Cloud project ID for Vertex AI client billing and resource scoping. |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | GCP region location for hosting models and accessing regional buckets. |
| `GOOGLE_GENAI_USE_VERTEXAI`| `True` | Flags whether to use the Vertex AI standard API (Enterprise) vs the Google GenAI SDK direct. |
| `DATABASE_URL` | `postgresql://...` | Connection URI for the Cloud SQL PostgreSQL instance supporting RAG `pgvector`. |
| `GCS_KNOWLEDGE_BUCKET` | `studymateai-knowledge-docs`| The target Cloud Storage bucket storing raw textbook notes/PDF files. |
| `MODEL_NAME` | `gemini-2.5-flash-lite`| Model selection for doubt resolution, quizzes, and reviews. |
| `EMBEDDING_MODEL` | `text-embedding-004` | Model selection for encoding search documents and queries. |
| `APP_ENV` | `development` | Target deployment environment stage (`development`, `staging`, `production`). |
| `LOG_LEVEL` | `INFO` | Output log verbosity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `MAX_RAG_CHUNKS` | `3` | Maximum matching chunks retrieved during RAG vector search to limit token consumption. |
| `MAX_RESPONSE_TOKENS` | `2048` | Upper token generation boundary for Vertex LLM calls to control latency and costs. |
| `ENABLE_INTERNET_AGENT` | `False` | Gating flag for routing queries to external web search models (MVP is offline-only). |
| `ENABLE_PERSONALIZATION` | `False` | Gating flag for personalizing responses based on historical progress metrics. |

---

## 🛡️ Enterprise Security & Guardrails

To meet enterprise production security standards, StudyMateAI implements strict access and input controls:
1. **Prompt & Input Sanitization**: The `PromptGuard` module detects prompt injection, SQL injection, and system instruction override attempts inside student queries before routing them to Vertex AI.
2. **Container Security**: The Cloud Run backend container executes under a dedicated non-root user (`appuser:appgroup`), mitigating host escalation risks.
3. **Secret Gating**: No API keys or service account credentials are hardcoded. Cloud Run accesses SQL connection credentials dynamically from **GCP Secret Manager** using IAM service account bindings.
4. **Pedagogical Boundary Enforcements**: LLM output configurations enforce schema validation (via Pydantic and JSON schemas) for all quiz generations, preventing hallucinated format schemas.

---

## 📊 Observability & Auditing

- **Structured Auditing**: Every transaction is logged with correlation IDs tracing the student ID, active metadata inputs (subject, year, board), request latencies, and token usage metrics.
- **Firestore Logs**: All generated quizzes, answers, evaluation history, and student progress indices are recorded in Firestore DB to maintain audit histories.
- **Error Tracking**: Connection drops (e.g. database connection failures or model timeouts) fallback gracefully to offline mock curriculum indices and log detailed stack traces to GCP Cloud Logging.

---

## 🧪 CI/CD & Quality Gating

Prior to pushing releases to production, the codebase undergoes the following quality verification checks:
1. **Automated Testing Suite**: Execute `pytest tests/` in the root workspace to run 25 API, CLI, and integration test cases covering route detection, agent processing, and response limits.
2. **Type Checking & Linting**: Codebase validation via Next.js compiler checks (`npm run build`) and Python type hinting ensuring type safety across client-server communications.
3. **Branch Protections**: Commits are gated behind automated build triggers verifying container integrity before pushing the latest tag to Artifact Registry.

---

## 💾 Local Vector Database Setup

Since the RAG Agent uses `pgvector` for similarity searches, you will need a running PostgreSQL database with the vector extension installed.

### 🐳 Run via Docker (Recommended)
You can spin up an instance locally using the `ankane/pgvector` Docker image:
```bash
docker run --name studymateai-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=studymateai \
  -p 5432:5432 \
  -d ankane/pgvector:latest
```

Once running, you can connect to your local database using client tools or the FastAPI server using the default `DATABASE_URL` configured in `app/core/config.py`:
`postgresql://postgres:postgres@localhost:5432/studymateai`

---

## 🔍 Troubleshooting & FAQ

### 1. `Connection refused (0x0000274D/10061)` / PostgreSQL connection offline
* **Symptoms**: The console logs show: `VectorStore database connection refused or offline. Falling back to curriculum mock grounding data.`
* **Solution**: Ensure your local PostgreSQL Docker container is running:
  ```bash
  docker start studymateai-postgres
  ```
  If you are running PostgreSQL natively, verify that the service is running on port `5432` and accepting connections.

### 2. Vertex AI Credential Errors
* **Symptoms**: Authentication errors when calling Gemini or Embedding models (`DefaultCredentialsError`).
* **Solution**: Make sure you have authorized the Google Cloud SDK CLI and set up application default credentials locally:
  ```bash
  gcloud auth application-default login
  ```
  This creates a credentials file that the local Google Cloud Python SDK reads automatically.

### 3. Firebase Deployment Permission Denied
* **Symptoms**: Firebase Hosting deployment fails with authentication errors.
* **Solution**: Re-authenticate the Firebase CLI:
  ```bash
  npx firebase logout
  npx firebase login
  ```
  Ensure that your logged-in Google account has appropriate IAM Owner/Editor permissions on the target Firebase project.

---

## 🖼️ Application Showcase Screenshots

Here are the screenshots showing the fully deployed StudyMateAI dashboard in action. 
### Quiz 
![Learning Context & Doubt Solver](docs/screenshots/quiz.png)

### Self Assessment Result
![Learning Context & Doubt Solver](docs/screenshots/self-assessment.png)

### NEET Exam Style Quiz
![Learning Context & Doubt Solver](docs/screenshots/quiz-neet.png)

### Self Assessment Result
![Learning Context & Doubt Solver](docs/screenshots/self-assessment-neet.png)

### KCET Exam Style Quiz
![Learning Context & Doubt Solver](docs/screenshots/quiz-kcet.png)

### Self Assessment Result
![Learning Context & Doubt Solver](docs/screenshots/self-assessment-kcet.png)




### 1. Student Ask
(Due to the length of the dashboard, the interface is captured in three consecutive screenshots):

![Learning Context & Doubt Solver](docs/screenshots/01-doubt-solving-response.png)
![Practice Questions & Entrance Exam Style](docs/screenshots/02-quiz-generation-view.png)
![Related Topics & Reference Sources](docs/screenshots/03-evaluation-grades-feedback.png)



