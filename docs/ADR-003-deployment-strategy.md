# Architecture Decision Record (ADR) - 003: Deployment & Hosting Topology

## Status
Approved

## Context
The MVP requires hosting that scales to zero to minimize idle infrastructure costs, supports secure HTTPS out-of-the-box, and easily hooks up with GCP services like Secret Manager and Cloud SQL.

## Decision
We deploy StudyMateAI using serverless GCP architecture:
- **Backend API**: FastAPI containerized and deployed to **Google Cloud Run**.
  - Auto-scaling limits: `min-instances = 0` (scales to zero when idle) and `max-instances = 2` (limits budget footprint).
- **Frontend Client**: Next.js compiled to static HTML assets and deployed on **Firebase Hosting** for global edge performance.
- **Secrets Management**: Database passwords and API keys are stored in **GCP Secret Manager** and injected into Cloud Run at runtime (no secrets in repository).

## Consequences
- **Pros**: Scales to zero (near-zero baseline cost), robust security boundaries, and simple deployment scripts.
- **Cons**: Occasional cold starts (up to 3-5 seconds) when scaling from zero.
