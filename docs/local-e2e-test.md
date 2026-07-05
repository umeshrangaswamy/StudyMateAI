# StudyMateAI Local End-To-End Test Guide

This document details the step-by-step instructions to configure, run, and verify the StudyMateAI platform locally.

---

## 1. Environment Configuration

Create a `.env` file inside `apps/backend/` containing:
```ini
# GCP configurations
GOOGLE_CLOUD_PROJECT=studymateai-dev
GOOGLE_CLOUD_LOCATION=asia-south1

# Cloud SQL PostgreSQL database connection URL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/studymateai

# Gemini API configuration
MODEL_NAME=gemini-1.5-flash
EMBEDDING_MODEL=text-embedding-004

# App config
APP_ENV=development
LOG_LEVEL=INFO

# Cost Controls
MAX_RAG_CHUNKS=3
MAX_RESPONSE_TOKENS=700
ENABLE_INTERNET_AGENT=false
ENABLE_PERSONALIZATION=false
```

---

## 2. Running the Backend Locally

1. Open a terminal and navigate to the project root:
   ```powershell
   # Activate Python Virtual Environment
   .venv\Scripts\Activate.ps1
   ```
2. Start the FastAPI Uvicorn backend server:
   ```powershell
   cd apps/backend
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```
3. Verify liveness by loading `http://localhost:8080/health` in your browser.

---

## 3. Running the Frontend Locally

1. Open a second terminal window and navigate to `apps/frontend/`:
   ```powershell
   cd apps/frontend
   ```
2. Configure environment variable mapping:
   ```powershell
   $env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8080"
   ```
3. Start the Next.js development server:
   ```powershell
   npm run dev
   ```
4. Load the dashboard in your browser at `http://localhost:3000`.

---

## 4. Execution of E2E Test Prompts

Execute the following test cases in the prompt textarea on `http://localhost:3000` to verify correct routing and processing:

### Case 1: Physics Query
* **Input settings**: Year = `2nd PUC`, Board = `Karnataka State Board`, Subject = `Physics`
* **Prompt**: `Explain Ray Optics for NEET`
* **Expected Result**: routes to Physics SME. Response contains simple Ray Optics explanation grounded in textbook context.

### Case 2: Chemistry Query
* **Input settings**: Year = `2nd PUC`, Board = `Karnataka State Board`, Subject = `Chemistry`
* **Prompt**: `Explain Chemical Bonding for KCET`
* **Expected Result**: routes to Chemistry SME. Response contains Chemical Bonding overview focusing on application-based KCET parameters.

### Case 3: NEET Quiz Query
* **Input settings**: Year = `2nd PUC`, Board = `Karnataka State Board`, Subject = `Physics`
* **Prompt**: `Generate 5 NEET MCQs on Refraction`
* **Expected Result**: routes to Quiz Generator. Response panel renders 5 MCQs quiz questions with options A, B, C, D, and detailed explanations.

### Case 4: Evaluation Query
* **Input settings**: Year = `2nd PUC`, Board = `Karnataka State Board`, Subject = `Chemistry`
* **Prompt**: `Evaluate my answer: ionic bond is formed by sharing electrons`
* **Expected Result**: routes to Evaluator agent. Output shows a grading score (e.g. `0/10` or `1/10`), identifies that sharing is covalent rather than ionic (missing concept: *electron transfer*), and provides encouraging tips to revise ionic definitions.

---

## 5. Verification Checkpoints

### 5.1 Verification of Structured JSON Logs
Inspect stdout terminal logs from the backend. Verify that log entries are printed as structured JSON lines containing:
* `request_id` (UUID key matching incoming headers)
* `subject`, `board`, `year`
* `detected_intent`, `detected_exam`
* `agent_path` (e.g. `orchestrator -> RAG -> PhysicsSME`)
* `latency_ms` (execution runtime timing)
* `model_name` (`gemini-1.5-flash`)
* `error_type` (`none` on successes)

*Check that API credentials, passwords, and user raw queries are masked or absent in telemetry fields.*

### 5.2 Verification of RAG Grounding
When textbooks are ingested, inspect `sources` metadata elements rendered inside the frontend answer cards. Grounding source links should show title (e.g., `Ray Optics Textbook`), chapter, and page references, verifying pgvector similarities matched correctly.
