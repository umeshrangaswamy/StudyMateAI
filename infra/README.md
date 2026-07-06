# StudyMateAI Infrastructure Management

This directory manages the provisioning and orchestration of Google Cloud Platform (GCP) resources for the StudyMateAI MVP.

## 📁 Directory Structure

- **`terraform/`**: Infrastructure as Code (IaC) configuration files using Terraform. Sets up:
  - Google Cloud Run (hosting the FastAPI backend with min instances = 0, max = 2 limits).
  - Cloud SQL PostgreSQL instance configured with `pgvector` compatibility and low-cost instances (`db-f1-micro`).
  - Google Cloud Storage (GCS) buckets for curriculum textbook uploads.
  - Firestore databases for tracking transaction logs and progress profiles.
- **`gcloud/`**: Initialization helper bash scripts for sequential step-by-step setup and deployment.
