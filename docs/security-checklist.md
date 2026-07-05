# StudyMateAI Security Checklist & Guidelines

This document details the security constraints, access control policies, and threat mitigation models implemented for the StudyMateAI Free Tier / Starter platform.

---

## 1. Cloud & IAM Infrastructure Security

### 1.1 IAM Least Privilege
* All administrative roles are isolated. System operators must only run scripts using credentials bound with the narrowest scope required to execute.
* Automatic API enablement (`01-enable-apis.sh`) and resource provisioning run under explicitly configured project scopes.

### 1.2 Cloud Run Service Account
* Deploys the FastAPI container utilizing a dedicated service account identity (`study-buddy-runner`).
* Minimum permission roles bound:
  * `roles/secretmanager.secretAccessor` (read `DATABASE_URL` credentials)
  * `roles/aiplatform.user` (interact with Vertex AI Gemini & embedding API endpoints)
  * `roles/cloudsql.client` (connect to Cloud SQL PostgreSQL instance auth proxies)
  * `roles/datastore.user` (read/write logs inside Firestore db namespaces)
  * `roles/storage.objectViewer` (read curriculum textbook grounding documents from Storage)

### 1.3 Secret Manager
* Confidential connection strings and credentials (such as database proxy parameters) are stored inside GCP Secret Manager as encrypted secret keys. They are not injected in raw text during build configurations.

### 1.4 No Hardcoded Secrets
* No database passwords, API credentials, GCP service keys, or private parameters are hardcoded in the codebase.
* The application loads configuration from environment variables via Pydantic `BaseSettings`. Local development parameters utilize a `.gitignored` `.env` config file.

### 1.5 CORS Policy
* The FastAPI backend configures CORS rules (`CORSMiddleware`) allowing verified origins to connect, preventing cross-origin execution exploits in production environments.

### 1.6 Database Access Controls
* Cloud SQL PostgreSQL instances are configured to deny direct public TCP connections. Access is restricted using secure Cloud SQL Auth Proxies via Unix sockets.
* Database query transactions utilize parameterized inputs, preventing SQL injection vulnerabilities.

### 1.7 Firestore Rules
* Access rules on the Firestore schema restrict write requests to authenticated operations matching active workspace service context. User transactions are logged via backend service calls, preventing client-side database write access.

---

## 2. LLM & Application Threat Protection

### 2.1 Prompt Injection Guard
* Every query is scanned deterministically by `PromptGuard` before routing or invoking Vertex AI services.
* Blocks queries containing system override instructions, malicious commands, or credential extraction prompts.

### 2.2 Input Validation
* Input payloads are validated by Pydantic models (`AskRequest`):
  * Rejects empty prompts or queries consisting only of whitespace.
  * Rejects out-of-scope parameters to prevent unindexed scans.

### 2.3 Output Filtering
* Formatter systems evaluate output data structures to ensure JSON blocks conform to schemas.

### 2.4 Cloud Logging Safety
* Logging formatting utilities (`JSONFormatter`) run sanitizing scans:
  * Masks connection strings, passwords, auth bearer headers, and API keys.
  * Redacts complete system prompts or internal agent instructions.
  * Excludes raw student prompt inputs from structured fields to protect student PII.

### 2.5 No System Prompt Leakage
* SME agent prompts and internal instructions are separated into distinct templates under `packages/prompts/`.
* PromptGuard and orchestrator components block queries attempting to extract instructions, preventing leakage.

### 2.6 No Unsupported Subject Routing
* Free Tier boundaries enforce a strict whitelist (Physics and Chemistry only).
* Pydantic validators reject requests targeting unsupported subjects (e.g. Mathematics, Biology) before any execution.

### 2.7 No Unrestricted Internet Access
* No internet search tools (such as the Internet Research Agent) are deployed or active in the Free Tier.
* All grounding details are retrieved from localized, verified curriculum sources stored inside pgvector databases.
