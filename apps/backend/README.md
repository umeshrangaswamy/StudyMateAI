# StudyMateAI Backend API Service

This is the backend API service for **StudyMateAI (Free Tier)**. It is built with **FastAPI** (Python 3.11) and designed to run serverless on **Google Cloud Run**.

## 🏗️ Architecture & Modules

The backend implements a modular multi-agent structure:
- **`app/api/endpoints.py`**: Defines HTTP entry points (`/chat`, `/quiz`, `/evaluate`) and validation schemas.
- **`app/agents/`**: Houses agent classes acting in sequence (`OrchestratorAgent` -> `RAGAgent` -> `PhysicsSMEAgent`/`ChemistrySMEAgent` -> `EvaluatorAgent`).
- **`app/core/`**: Configuration management using Pydantic Settings.

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.11 installed
- Local PostgreSQL with `pgvector` extension (optional for basic skeleton testing)

### 2. Setup Virtual Environment
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

### 3. Start the FastAPI Server
```bash
# From the backend directory, run:
uvicorn main:app --reload --port 8080
```
Visit http://127.0.0.1:8080/docs in your browser to view the interactive Swagger documentation.

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
