# Volume 3 – GCP Architecture & Infrastructure Design
## StudyMateAI– GCP Native Architecture (Version 1.0)

## 1. Purpose
This document maps StudyMateAIproduct and agent architecture to Google Cloud infrastructure.

Goal:
- MVP: production-grade structure with minimal cost for 0–10 users
- Enterprise: scalable architecture without redesign

## 2. Infrastructure Principles
1. Serverless first
2. Same core architecture from MVP to production
3. Cloud Run before GKE
4. PostgreSQL + pgvector from Day 1
5. Metadata-first RAG
6. Minimal free-tier components
7. Enterprise controls added later

## 3. MVP Architecture
```text
Next.js Static Frontend
  -> Firebase Hosting
  -> Cloud Run Backend
      -> Orchestrator
      -> Physics SME
      -> Chemistry SME
      -> RAG Agent
      -> Quiz Generator
      -> Evaluator
  -> Vertex AI Gemini Flash
  -> Vertex AI Embeddings
  -> Cloud SQL PostgreSQL + pgvector
  -> Cloud Storage
  -> Firestore
  -> Cloud Logging / Monitoring
```

## 4. Enterprise Architecture
```text
Users
  -> Cloud Armor
  -> Apigee API Gateway
  -> Load Balancer
  -> Cloud Run / GKE
      -> Orchestrator Service
      -> SME Services
      -> RAG Service
      -> Quiz Service
      -> Evaluator Service
      -> Personalization Service
  -> Vertex AI
  -> Cloud SQL HA + pgvector / Vertex AI Vector Search if needed
  -> Cloud Storage
  -> Memorystore Redis
  -> BigQuery
  -> Cloud Operations Suite
```

## 5. Frontend Architecture
### MVP
- Next.js
- TypeScript
- Tailwind CSS
- Static export
- Firebase Hosting
- No SSR
- No authentication initially

### Enterprise
- Firebase Hosting / App Hosting / Cloud CDN
- Authentication
- Dashboard
- Study planner
- Progress analytics

## 6. Backend Architecture
### MVP
Single Cloud Run service:
```text
study-buddy-api
```

Contains:
- API endpoints
- Agent orchestration
- RAG logic
- Vertex AI service integration
- pgvector retrieval
- evaluator

Cloud Run settings:
- min instances: 0
- max instances: 2
- memory: 512Mi initially
- CPU: 1

### Enterprise
Split services when required:
- orchestrator-service
- rag-service
- academic-sme-service
- quiz-service
- evaluator-service
- personalization-service

## 7. AI Platform
### MVP
- Gemini Flash for generation
- text-embedding-004 for embeddings
- Rule-based routing where possible to reduce model calls

### Enterprise
- Hybrid SLM/LLM strategy
- Gemini Flash for most tasks
- Gemini Pro for complex tasks
- Gemma or other SLMs for routing and low-cost tasks where practical

## 8. Data Services
### MVP
- Cloud Storage for documents
- Cloud SQL PostgreSQL + pgvector for chunks and embeddings
- Firestore for lightweight user/session metadata

### Enterprise
- Cloud SQL HA
- Read replicas
- BigQuery analytics
- Redis cache
- Data lifecycle policies

## 9. RAG Infrastructure
### MVP
```text
Cloud Storage documents
  -> Ingestion pipeline
  -> Chunking
  -> Embedding generation
  -> PostgreSQL + pgvector
  -> RAG Agent
  -> SME Agent
```

### Enterprise
- More automated ingestion
- Document AI optional
- Advanced evaluation
- Vertex AI Vector Search only if pgvector scale becomes insufficient

## 10. Networking
### MVP
```text
Internet -> Firebase Hosting -> Cloud Run -> Cloud SQL / Vertex AI / Cloud Storage
```

### Enterprise
```text
Internet -> Cloud Armor -> Apigee -> Load Balancer -> Private VPC -> Services
```

## 11. Authentication
### MVP
- Optional no-login for private testing
- Firebase Auth when needed

### Enterprise
- Identity Platform
- OAuth2/OIDC
- Enterprise SSO
- RBAC

## 12. Security
### MVP
- IAM least privilege
- Cloud Run service account
- Secret Manager
- Firestore rules
- Prompt guard
- Vertex AI safety settings
- HTTPS by default

### Enterprise
- Cloud Armor
- Apigee
- DLP API
- KMS
- Security Command Center
- VPC Service Controls where needed

## 13. Observability
### MVP
- Cloud Logging
- Cloud Monitoring
- Structured logs
- Latency
- Errors
- Token estimates
- Agent path

### Enterprise
- OpenTelemetry
- Prometheus
- Grafana
- Model quality dashboards
- Hallucination sampling
- Cost analytics

## 14. CI/CD
### MVP
- GitHub Actions
- Backend test and deploy to Cloud Run
- Frontend build and Firebase deploy

### Enterprise
- Dev/test/prod environments
- Workload Identity Federation
- Canary / blue-green deployment
- Security scanning
- IaC with Terraform

## 15. Environment Strategy
### MVP
- Local
- Dev GCP project

### Enterprise
- dev
- test
- uat
- prod
- separate projects and service accounts

## 16. Cost Controls
- Cloud Run min instances = 0
- Cloud Run max instances = 2
- RAG top_k = 3
- Gemini output token limits
- No Redis in MVP
- No GKE in MVP
- No Apigee in MVP
- No Cloud Armor in MVP
- Smallest practical Cloud SQL instance

## 17. Locked Infrastructure Decisions
- Cloud Run for backend
- Firebase Hosting for light UI
- Cloud SQL PostgreSQL + pgvector from Day 1
- Cloud Storage for curriculum documents
- Vertex AI for Gemini and embeddings
- Firestore for metadata
- No ChromaDB / Pinecone in MVP
