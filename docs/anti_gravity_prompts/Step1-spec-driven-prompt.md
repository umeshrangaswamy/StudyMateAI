
## Task 1 — Create Repository Skeleton

Use this first.

```text
You are my senior AI agent developer inside Antigravity IDE.

Read:
- AGENTS.md
- docs/volume-1-product-architecture.md
- docs/volume-2-agent-architecture.md
- docs/volume-3-gcp-architecture.md
- docs/volume-4-data-rag-architecture.md

Implement My Study Buddy Free Tier architecture only.

Important:
- User base: 0–10
- Production-grade structure
- Minimal cost
- Frontend: lightweight Next.js static UI
- Backend: FastAPI on Cloud Run
- AI: Vertex AI Gemini Flash
- Embeddings: Vertex AI text embeddings
- Vector DB: Cloud SQL PostgreSQL + pgvector
- Storage: Cloud Storage
- Metadata: Firestore
- Agents: Orchestrator, Physics SME, Chemistry SME, RAG Agent, Quiz Generator, Evaluator
- Subjects implemented: Physics and Chemistry only
- Exams implemented: KCET and NEET only
- Do not add GKE, Apigee, Redis, ChromaDB, Pinecone, or Vertex Vector Search for free tier.

First task:
Create the repository skeleton, README files, backend and frontend placeholders, and explain what you created before implementing business logic.

Expected structure:
my-study-buddy/
  apps/
    frontend/
    backend/
  packages/
    prompts/
    shared/
  scripts/
    ingestion/
  infra/
    gcloud/
    terraform/
  docs/
  tests/
  .github/
    workflows/
```

### What you should check after Task 1

Verify that Antigravity created:

```text
apps/frontend/
apps/backend/
packages/prompts/
packages/shared/
scripts/ingestion/
infra/gcloud/
infra/terraform/
.github/workflows/
```

Do not continue until this structure is clean.

***

## Task 2 — Create Backend FastAPI Shell

```text
Read AGENTS.md and all architecture docs.

Now implement only the backend FastAPI shell inside apps/backend.

Create:
- main.py
- app/core/config.py
- app/core/logging.py
- app/models/request_models.py
- app/models/response_models.py
- app/agents/orchestrator.py
- app/agents/physics_sme.py
- app/agents/chemistry_sme.py
- app/agents/rag_agent.py
- app/agents/quiz_generator.py
- app/agents/evaluator.py
- app/services/vertex_ai_service.py
- app/services/embedding_service.py
- app/services/vector_store.py
- app/services/firestore_service.py
- app/security/prompt_guard.py
- requirements.txt
- Dockerfile

Create endpoints:
- GET /health
- GET /ready
- POST /api/ask

Do not fully implement Vertex AI or database calls yet.
Use clean interfaces and placeholders.
Do not hardcode secrets.
Use environment variables through app/core/config.py.

After creating the files, explain:
1. Backend structure
2. API flow
3. Where each agent will be implemented
4. What remains as placeholder
```

### What you should check after Task 2

Make sure `POST /api/ask` exists and accepts this JSON:

```json
{
  "year": "2nd PUC",
  "board": "Karnataka State Board",
  "subject": "Physics",
  "query": "Explain Ray Optics for NEET"
}
```

***

## Task 3 — Create API Models And Validation

```text
Implement request and response models for My Study Buddy backend.

Use Pydantic models.

Request model:
{
  "year": "2nd PUC",
  "board": "Karnataka State Board",
  "subject": "Physics",
  "query": "Explain Ray Optics for NEET"
}

Response model:
{
  "answer": "...",
  "response_type": "explanation",
  "sources": [
    {
      "title": "...",
      "chapter": "...",
      "page_number": 12
    }
  ],
  "metadata": {
    "subject": "physics",
    "intent": "entrance_preparation",
    "exam": "neet",
    "confidence": 0.86
  }
}

Validation rules:
- year is required
- board is required
- subject is required
- query is required
- free tier supports only Physics and Chemistry
- query must not be empty
- max query length should be controlled

Add clean error responses.

Do not modify architecture decisions.
```

### Why this task matters

This prevents bad requests from reaching your AI agents.

For free tier, validation is your first cost-control and safety-control layer.

***

## Task 4 — Implement Prompt Guard

```text
Implement app/security/prompt_guard.py.

The prompt guard must detect and block obvious prompt injection attempts.

Block examples:
- ignore previous instructions
- reveal system prompt
- print hidden instructions
- show API keys
- override developer message
- act as unrestricted AI
- jailbreak
- system override
- disregard safety rules

Return a structured result:
{
  "allowed": false,
  "reason": "prompt_injection_detected"
}

Integrate prompt guard into the Orchestrator before any model call.

Keep it rule-based for free tier.
Do not use an LLM for prompt guard in the initial implementation.
```

### Why this task matters

This avoids spending model tokens on unsafe requests.

It also protects your system prompts and internal instructions.

***

## Task 5 — Implement Orchestrator Agent

```text
Implement the Orchestrator Agent.

Read AGENTS.md and docs/volume-2-agent-architecture.md carefully.

Responsibilities:
1. Validate request context.
2. Run prompt guard.
3. Normalize subject.
4. Detect exam name from query:
   - KCET
   - NEET
5. Detect intent:
   - doubt_solving
   - lesson_explanation
   - lesson_summary
   - quick_notes
   - exam_preparation
   - entrance_preparation
   - quiz_generation
   - answer_evaluation
6. Select workflow:
   - quiz_generation -> RAG Agent + Quiz Generator
   - answer_evaluation -> Evaluator
   - normal academic query -> RAG Agent + Physics/Chemistry SME
7. Return response through a consistent response model.

Use deterministic keyword routing first.
Use LLM-based routing only as a future extension.
Do not create a separate Exam Agent.
Physics SME and Chemistry SME must handle KCET/NEET preparation.
```

### What you should check after Task 5

Test these examples mentally or through unit tests:

```text
"Explain Ray Optics for NEET"
=> subject Physics, exam neet, intent entrance_preparation

"Generate KCET quiz on Chemical Bonding"
=> subject Chemistry, exam kcet, intent quiz_generation

"Evaluate my answer: ionic bond is formed by sharing electrons"
=> intent answer_evaluation
```

***

## Task 6 — Implement Prompt Files

```text
Create prompt files under packages/prompts.

Files:
- global_system.md
- physics_sme.md
- chemistry_sme.md
- rag_agent.md
- quiz_generator.md
- evaluator.md

Move agent instructions into these prompt files.

Rules:
- Do not hardcode long prompts inside Python files.
- Backend should load prompts from packages/prompts.
- Add prompt version metadata at the top of each file.
- Prompts must follow educational boundaries from volume 1.
- Prompts must instruct agents to stay within selected year, board, subject, and exam scope.
```

### Why this task matters

Prompt files become version-controlled artifacts.

Later you can evaluate prompt versions independently.

***

## Task 7 — Implement Physics SME Agent

```text
Implement Physics SME Agent.

Read:
- docs/volume-1-product-architecture.md
- docs/volume-2-agent-architecture.md
- packages/prompts/physics_sme.md

Physics SME must support:
- doubt solving
- lesson explanation
- quick notes
- lesson summary
- board exam preparation
- KCET preparation
- NEET preparation
- formula explanation
- numerical guidance

Input:
- year
- board
- subject
- query
- detected intent
- detected exam
- RAG context
- sources

Response style:
1. Short heading
2. Simple explanation
3. Real-life example
4. Formula if applicable
5. KCET/NEET tip if exam is detected

Rules:
- Use RAG context.
- Stay inside academic scope.
- Keep answer crisp.
- If RAG context is insufficient, say so clearly.
```

### What you should check

Physics SME should not behave like a generic chatbot.

It must behave like a Physics teacher and exam coach.

***

## Task 8 — Implement Chemistry SME Agent

```text
Implement Chemistry SME Agent.

Read:
- docs/volume-1-product-architecture.md
- docs/volume-2-agent-architecture.md
- packages/prompts/chemistry_sme.md

Chemistry SME must support:
- doubt solving
- concept explanation
- quick notes
- lesson summary
- board exam preparation
- KCET preparation
- NEET preparation
- reaction explanation
- equation explanation

Input:
- year
- board
- subject
- query
- detected intent
- detected exam
- RAG context
- sources

Response style:
1. Short heading
2. Concept
3. Explanation
4. Chemical example or equation if required
5. KCET/NEET tip if exam is detected

Rules:
- Use RAG context.
- Stay inside academic scope.
- Keep answer crisp.
- Do not invent chemical facts outside the retrieved context.
```

***

## Task 9 — Implement Vertex AI Service

```text
Implement app/services/vertex_ai_service.py.

Use environment variables:
- GOOGLE_CLOUD_PROJECT
- GOOGLE_CLOUD_LOCATION
- GOOGLE_GENAI_USE_VERTEXAI=true
- MODEL_NAME
- EMBEDDING_MODEL

Create methods:
1. generate_text(system_instruction, prompt, temperature, max_tokens)
2. generate_json(system_instruction, prompt, schema)
3. estimate_tokens_if_possible(prompt)

Use Gemini Flash for generation.

Rules:
- Do not hardcode API keys.
- Use Application Default Credentials.
- Keep max token output configurable.
- Log model name, latency, and errors.
- Do not log full prompts in production-style logs.
```

### Why this task matters

This centralizes all LLM calls.

All agents should call this service instead of directly calling Vertex AI.

***

## Task 10 — Implement Embedding Service

```text
Implement app/services/embedding_service.py.

Use configured Vertex AI embedding model.

Create method:
- embed_text(text: str) -> list[float]

Rules:
- Validate text is non-empty.
- Truncate extremely long text before embedding.
- Log embedding request metadata, not full content.
- Do not embed user PII or secrets.
- Keep embedding model configurable through environment variable.
```

***

## Task 11 — Implement PostgreSQL + pgvector Schema

```text
Create SQL migration files under apps/backend/migrations.

Create:
- 001_extensions.sql
- 002_documents.sql
- 003_chunks.sql
- 004_embeddings.sql
- 005_assessments.sql
- run_migrations.py

Required tables:
1. documents
2. curriculum_chunks
3. chunk_embeddings
4. student_assessments

Required extensions:
- vector
- uuid-ossp or pgcrypto

Indexes:
- subject
- board
- year
- chapter
- exam
- vector index if appropriate

Important:
Use vector dimension as a configurable constant or document clearly that it must match the embedding model output.
```

***

## Task 12 — Implement Vector Store Service

```text
Implement app/services/vector_store.py.

Responsibilities:
1. Connect to PostgreSQL.
2. Run metadata-filtered vector search.
3. Return top-k chunks.
4. Include source metadata.
5. Never search all subjects without filters.

Method:
search_chunks(
  query_embedding,
  subject,
  board,
  year,
  exam=None,
  chapter=None,
  top_k=3
)

SQL must filter before ordering by vector distance.

Return:
[
  {
    "content": "...",
    "title": "...",
    "chapter": "...",
    "topic": "...",
    "page_number": 12,
    "distance": 0.21
  }
]
```

***

## Task 13 — Implement RAG Agent

```text
Implement RAG Agent.

Responsibilities:
1. Accept normalized request from Orchestrator.
2. Generate query embedding using Embedding Service.
3. Search PostgreSQL + pgvector using Vector Store.
4. Apply metadata filters:
   - subject
   - board
   - year
   - optional exam
   - optional chapter if detected
5. Return top 3 chunks.
6. Compress or format context for SME Agent.
7. Return source references.

Rules:
- Do not answer the student directly.
- RAG Agent retrieves and prepares context only.
- If no chunks found, return empty context with clear retrieval status.
```

***

## Task 14 — Implement Quiz Generator Agent

```text
Implement Quiz Generator Agent.

Input:
- year
- board
- subject
- query
- detected exam
- RAG context
- sources

Capabilities:
- Generate KCET-style quiz
- Generate NEET-style quiz
- Generate general chapter quiz

Default free-tier quiz:
- 5 MCQs
- 4 options per question
- correct answer
- short explanation

Output must be structured JSON:
{
  "quiz": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "B",
      "explanation": "..."
    }
  ]
}

Rules:
- Use RAG context.
- Keep questions within selected subject and exam scope.
- Do not generate unsupported questions.
```

***

## Task 15 — Implement Evaluator Agent

```text
Implement Evaluator Agent.

Evaluator is part of Free Tier.

Capabilities:
1. Evaluate MCQ answers.
2. Evaluate short subjective answers.
3. Return score.
4. Identify missing points.
5. Suggest revision.

Input examples:
- "Evaluate my answer: ionic bond is formed by sharing electrons"
- "My answer is B"
- "Check this answer for NEET: ..."

Output:
{
  "score": 7,
  "max_score": 10,
  "feedback": "...",
  "missing_points": ["..."],
  "revision_tip": "..."
}

Rules:
- Use exact matching for MCQ if answer key is available.
- Use Gemini Flash only when subjective reasoning is needed.
- Keep feedback encouraging and concise.
```

***

## Task 16 — Implement Ingestion Pipeline

```text
Create ingestion pipeline under scripts/ingestion.

Files:
- extract_text.py
- chunk_text.py
- embed_and_load.py
- metadata_schema.json
- README.md

Input structure:
content/
  physics/
    ray-optics.txt
    ray-optics.metadata.json
  chemistry/
    chemical-bonding.txt
    chemical-bonding.metadata.json

Metadata example:
{
  "title": "Ray Optics Notes",
  "subject": "physics",
  "board": "Karnataka State Board",
  "year": "2nd PUC",
  "chapter": "Ray Optics",
  "exam": "NEET",
  "source": "internal-notes"
}

Pipeline:
1. Read document.
2. Read metadata.
3. Chunk text into approximately 300 tokens.
4. Use 10% overlap.
5. Generate embeddings.
6. Insert into documents table.
7. Insert into curriculum_chunks.
8. Insert into chunk_embeddings.

Do not ingest unsupported subjects in free tier.
```

***

## Task 17 — Implement Frontend UI

```text
Implement lightweight frontend in apps/frontend.

Use:
- Next.js
- TypeScript
- Tailwind CSS
- Static export friendly design

UI fields:
1. Year of Study dropdown
2. University / Board dropdown
3. Subject dropdown
4. Prompt text area
5. Submit button
6. Response panel

Supported subjects in UI:
- Physics
- Chemistry

Prompt field should allow user to mention:
- lesson
- chapter
- KCET
- NEET
- quiz
- exam preparation
- doubt

Call backend:
POST /api/ask

Use environment variable:
NEXT_PUBLIC_API_BASE_URL

Show:
- loading state
- error state
- answer
- response type
- sources
- metadata

Keep UI simple and low-cost.
Do not add login yet.
```

***

## Task 18 — Add Backend Unit Tests

```text
Create backend tests using pytest.

Test cases:
1. Valid Physics query routes to Physics SME.
2. Valid Chemistry query routes to Chemistry SME.
3. NEET query detects exam as neet.
4. KCET query detects exam as kcet.
5. Quiz query routes to Quiz Generator.
6. Evaluation query routes to Evaluator.
7. Prompt injection is blocked.
8. Unsupported subject is rejected.
9. Empty query is rejected.
10. RAG search applies metadata filters.

Mock:
- Vertex AI calls
- Database calls
- Embedding calls

Do not require real GCP services for unit tests.
```

***

## Task 19 — Add Frontend Tests

```text
Create frontend tests.

Test:
1. Page renders title My Study Buddy.
2. Year dropdown renders.
3. Board dropdown renders.
4. Subject dropdown renders.
5. Prompt text area renders.
6. Submit button is disabled if required fields are empty.
7. Submit button calls backend when all fields are present.
8. Response panel displays answer.
9. Error message displays on backend failure.

Keep tests lightweight.
```

***

## Task 20 — Add GCP Setup Scripts

```text
Create scripts under infra/gcloud.

Files:
- 01-enable-apis.sh
- 02-create-bucket.sh
- 03-create-cloudsql.sh
- 04-create-service-account.sh
- 05-create-secrets.sh
- 06-deploy-cloudrun.sh
- README.md

Scripts must support environment variables:
- PROJECT_ID
- REGION
- DB_INSTANCE
- DB_NAME
- SERVICE_NAME
- BUCKET_NAME

Free-tier defaults:
- REGION=asia-south1
- SERVICE_NAME=study-buddy-api
- Cloud Run min instances = 0
- Cloud Run max instances = 2

Do not include real passwords.
Use placeholders and instructions.
```

***

## Task 21 — Add Dockerfile

```text
Create production-ready Dockerfile for apps/backend.

Requirements:
- Python 3.11 slim base
- Install requirements
- Copy app code
- Use non-root user if practical
- Expose port 8080
- Start FastAPI with uvicorn
- Read PORT from environment variable if possible

Also add .dockerignore.
```

***

## Task 22 — Add GitHub Actions

```text
Create GitHub Actions workflows.

Files:
.github/workflows/backend-ci.yml
.github/workflows/frontend-ci.yml
.github/workflows/deploy-backend-cloudrun.yml
.github/workflows/security-scan.yml

backend-ci:
- install Python dependencies
- run lint if configured
- run pytest

frontend-ci:
- install npm dependencies
- run lint
- run build

deploy-backend-cloudrun:
- authenticate to Google Cloud
- deploy backend to Cloud Run
- use secrets and environment variables

security-scan:
- check for secrets
- run dependency scan if practical

Prefer Workload Identity Federation for production.
For free-tier learning, document service account JSON alternative but do not commit credentials.
```

***

## Task 23 — Add Observability

```text
Implement structured logging.

Log:
- request_id
- subject
- board
- year
- detected_intent
- detected_exam
- agent_path
- rag_chunks_found
- latency_ms
- model_name
- error_type

Do not log:
- API keys
- credentials
- full system prompts
- database password
- full student PII

Add middleware for request_id.
Add timing logs around agent execution.
```

***

## Task 24 — Add Cost Controls

```text
Create docs/cost-controls.md and implement relevant config.

Cost controls:
- Cloud Run min instances = 0
- Cloud Run max instances = 2
- RAG top_k = 3
- Limit model output tokens
- Use rule-based routing first
- Do not call evaluator unless evaluation intent is detected
- Do not call quiz generator unless quiz intent is detected
- Do not use Internet Research Agent in free tier
- Do not use Redis in free tier
- Do not use GKE in free tier
- Do not use Apigee in free tier

Add environment variables:
- MAX_RAG_CHUNKS=3
- MAX_RESPONSE_TOKENS=700
- ENABLE_INTERNET_AGENT=false
- ENABLE_PERSONALIZATION=false
```

***

## Task 25 — Add Security Checklist

```text
Create docs/security-checklist.md.

Include:
1. IAM least privilege
2. Cloud Run service account
3. Secret Manager
4. No hardcoded secrets
5. Prompt injection guard
6. Input validation
7. Output filtering
8. CORS policy
9. Firestore rules
10. Database access controls
11. Cloud Logging safety
12. No system prompt leakage
13. No unsupported subject routing
14. No unrestricted internet access in free tier
```

***

## Task 26 — End-To-End Local Test

```text
Create a local end-to-end test guide.

File:
docs/local-e2e-test.md

Include:
1. Start backend locally.
2. Configure .env.
3. Run frontend locally.
4. Submit Physics query.
5. Submit Chemistry query.
6. Submit NEET quiz query.
7. Submit KCET quiz query.
8. Submit evaluation query.
9. Verify logs.
10. Verify RAG retrieval if test data exists.

Use these test prompts:
- Explain Ray Optics for NEET
- Explain Chemical Bonding for KCET
- Generate 5 NEET MCQs on Refraction
- Evaluate my answer: ionic bond is formed by sharing electrons
```

***

## Task 27 — Deployment Readiness Review

```text
Review the complete codebase against AGENTS.md and architecture docs.

Check:
1. Only Physics and Chemistry are implemented.
2. Only KCET and NEET are implemented.
3. Orchestrator exists.
4. Physics SME exists.
5. Chemistry SME exists.
6. RAG Agent exists.
7. Quiz Generator exists.
8. Evaluator exists.
9. PostgreSQL + pgvector is used.
10. ChromaDB is not used.
11. Pinecone is not used.
12. Redis is not used.
13. GKE is not used.
14. Apigee is not used.
15. Cloud Run deployment exists.
16. Firebase frontend deployment exists.
17. Tests exist.
18. Cost controls exist.
19. Security checklist exists.

Generate a report:
docs/implementation-readiness-report.md
```

***