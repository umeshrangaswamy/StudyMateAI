# StudyMateAI Cost Controls & MVP Boundaries

This document details the cost optimization controls, resource caps, and agent routing logic implemented for the **MVP / Starter version** of StudyMateAI.

---

## 1. Cloud Infrastructure Caps
To prevent unintended resource scaling charges under the MVP:
* **Cloud Run Instances Limits**:
  * `min-instances = 0`: Ensures the service scales to zero when idle, avoiding continuous runtime billing.
  * `max-instances = 2`: Caps total concurrent instances during traffic spikes.
* **Cloud SQL Micro Instance**:
  * Deployed utilizing the `db-f1-micro` tier bounds, which fit within low-cost/MVP limits.
* **Apigee, GKE, Cloud Armor & Redis**:
  * **Not deployed/used**: Bypassed for the MVP MVP to avoid high base hourly charges.

---

## 2. RAG & Database Retrieval Controls
* **MAX_RAG_CHUNKS (Default: 3)**:
  * Restricts pgvector metadata-filtered queries to return at most **3 chunks** per request.
  * Clamped programmatically inside the `RAGAgent.retrieve()` call.
* **Unindexed Global Table Scans Protection**:
  * Database query methods (`VectorStore.search_chunks`) throw validation exceptions if critical filters (`subject`, `board`, `year`) are missing, preventing unindexed table scans.

---

## 3. Vertex AI Model Cost Protections
* **MAX_RESPONSE_TOKENS (Default: 700)**:
  * Clamps generation configs (`max_output_tokens`) across all Vertex AI Gemini Flash text requests.
  * Enforced globally in `VertexAIService.generate_text()` to prevent long, expensive output streams.
* **Embedding Constraints**:
  * Input queries are trimmed/truncated before executing API embedding requests.

---

## 4. Deterministic Rule-Based Routing
To conserve LLM tokens, StudyMateAI implements deterministic, rule-based keyword intent checks *before* calling downstream AI agents:
1. **Security Scan**: `PromptGuard` runs a lightweight local rule check first to block malicious requests.
2. **Intent Branching**:
   * Evaluator Agent is **only** called when subjective/MCQ student answer structures are detected.
   * Quiz Generator Agent is **only** called when quiz request keywords are detected.
   * Unsupported subjects (e.g. biology) are rejected by Pydantic validation before routing to Vertex AI.

---

## 5. Environment Config Parameters
The following environment variables control cost configurations:
* `MAX_RAG_CHUNKS=3`
* `MAX_RESPONSE_TOKENS=700`
* `ENABLE_INTERNET_AGENT=false` (Disabled)
* `ENABLE_PERSONALIZATION=false` (Disabled)
