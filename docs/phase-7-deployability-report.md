# Phase 7: Deployability Showcase Report

## 1. Deployment Architecture Diagram

```mermaid
graph TD
    Student([Student Browser]) -->|HTTPS| FH[Firebase Hosting]
    Student -->|API Requests| CR[Cloud Run: study-buddy-api]
    
    subgraph Google Cloud Platform (GCP)
        CR -->|IAM Access| VX[Vertex AI: Gemini & Text Embeddings]
        CR -->|Secure Store| SM[Secret Manager: DATABASE_URL]
        CR -->|NoSQL Session Logging| FS[Firestore Database]
        
        CR -->|Cloud SQL Auth Proxy| SQL[(Cloud SQL: PostgreSQL + pgvector)]
        
        KB[(GCS: Knowledge Textbook Bucket)] <-->|Data Sync| SQL
    end
    
    subgraph CI/CD Pipeline
        GA[GitHub Actions] -->|Terraform Apply| GCP[Provision GCP Resources]
        GA -->|Docker Build & Push| CR
    end
```

---

## 2. Deployment Guide

### Cloud Run Parameters
*   **Service Name**: `study-buddy-api`
*   **Billing Strategy**: Minimum instances = 0 (scales to zero when idle to eliminate passive execution costs), Maximum instances = 2 (development throttle constraint).
*   **Resources**: CPU = 1, Memory = 512Mi.
*   **Platform**: Serverless container instance.

### Firebase Hosting Parameters
*   **Hosting Target**: Static export hosting.
*   **Build Output Directory**: `apps/frontend/out` (following `next build && next export` static export configuration).
*   **Redirections**: Clean routing fallback for single page application (SPA) paths.

### Terraform Configuration
*   Declared in `infra/terraform/main.tf`.
*   Resources Provisioned:
    *   `google_sql_database_instance`: PostgreSQL instance (`db-f1-micro` for MVP pricing).
    *   `google_storage_bucket`: GCS bucket for PDF curriculum source material.
    *   `google_cloud_run_v2_service`: API engine deployment config.

### GitHub Actions Workflows
*   `backend-ci.yml`: Unit test validation and Python syntax linting.
*   `frontend-ci.yml`: Static site generation build checks.
*   `deploy-backend-cloudrun.yml`: Authenticates via service keys or Workload Identity Federation, builds/tags backend container, pushes to GCR, and updates the Cloud Run service.

---

## 3. Reproducible Setup Guide

To bootstrap a new environment from scratch:

### Step 1: Initialise Google Cloud Project
Enable the required APIs (or run `infra/gcloud/01-enable-apis.sh`):
```bash
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com
```

### Step 2: Provision Infrastructure with Terraform
```bash
cd infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### Step 3: Run Ingest CLI for Textbook Materials
Prepare local database connection credentials, then run the CLI to build the vector store:
```bash
.\studymate.bat ingest "path/to/physics_textbook.pdf" --subject physics
.\studymate.bat ingest "path/to/chemistry_textbook.pdf" --subject chemistry
```

### Step 4: Configure CI/CD Secrets
Register these repository secrets on GitHub to allow automated deployments:
*   `GCP_PROJECT_ID`: Target Google Cloud Project ID.
*   `GCP_SA_KEY`: JSON service account credential key (with Cloud Run Admin, Storage Admin, and SQL Client permissions).
