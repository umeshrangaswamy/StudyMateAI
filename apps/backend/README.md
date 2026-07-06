# StudyMateAI Backend API Service

This is the backend API service for **StudyMateAI (MVP)**. It is built with **FastAPI** (Python 3.11) and designed to run serverless on **Google Cloud Run**.

The service incorporates the **Google Agent Development Kit (ADK)** to orchestrate specialized pedagogical agents.

## 🏗️ Architecture & Modules

The backend implements a modular multi-agent structure:
- **`app/api/endpoints.py`**: Defines HTTP entry points (`/api/ask`, `/health`, `/ready`) and compatibility endpoints for legacy routing interfaces.
- **`adk/`**: Houses Google ADK agents:
  - `root_agent.py` (`RootAgent`): Workflow director, intent detector, and security check router.
  - `physics_agent.py` (`PhysicsAgent`): Resolves Physics questions and generates formula sheets.
  - `chemistry_agent.py` (`ChemistryAgent`): Resolves Chemistry questions and formats equations.
  - `quiz_agent.py` (`QuizAgent`): Dynamically constructs syllabus-aligned MCQs.
  - `evaluator_agent.py` (`EvaluatorAgent`): Inspects generated material quality and evaluates student-submitted quiz/subjective responses.
  - `rag_agent.py` (`RAGAgent`): Fetches grounding material with strict curriculum metadata filters.
- **`adk/skills/`**: Domain skills repository providing decoupled, reusable pedagogical functions (e.g., `explain_concept`, `prepare_kcet`, `evaluate_quiz`). These are prime candidates for Model Context Protocol (MCP) server integration.
- **`app/core/`**: Configuration management using Pydantic Settings and Logging framework.

## 🚀 Running Locally

### 1. Setup Virtual Environment
```bash
# Navigate to the backend directory
cd apps/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the FastAPI Server
```bash
# Start server with reload enabled
uvicorn main:app --reload --port 8080
```
Visit http://127.0.0.1:8080/docs in your browser to view the interactive Swagger documentation.

## 💻 Unified Developer CLI

You can execute agent workflows directly from the terminal shell via `cli.py`:

```bash
# Ask a doubt (defaults to subject=physics)
python cli.py ask "What is ray optics?"

# Generate a syllabus quiz
python cli.py quiz --subject chemistry --year "2nd PUC"

# Evaluate answers against an MCQ set
python cli.py evaluate '[{"id": 1, "question": "...", "correct_option": "B"}]' '{"1": "B"}'

# Fetch student learning progress report
python cli.py progress --user_id "default_student"

# Ingest curriculum textbook file into Vector DB
python cli.py ingest "path/to/notes.txt" --subject chemistry
```

## 🐳 Docker Container Build

To build and run the backend inside a local Docker container:
```bash
# Build Docker image
docker build -t studymateai-backend .

# Run Docker container
docker run -p 8080:8080 studymateai-backend
```

## 🔐 Environment Configurations

Configurations can be overridden using environment variables or by creating a `.env` file in `apps/backend/`:
- `DATABASE_URL`: Cloud SQL connection string.
- `GCP_PROJECT_ID`: Target Google Cloud Project ID.
- `GCS_KNOWLEDGE_BUCKET`: Google Cloud Storage bucket containing syllabus/curriculum documents.
