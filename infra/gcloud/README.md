# StudyMateAI GCP Infrastructure Setup Scripts

This folder contains shell scripts to configure and deploy the StudyMateAI FastAPI backend to Google Cloud Platform (GCP).

## Directory Configuration
These setup scripts are located in:
`infra/gcloud/`

## Configuration Environment Variables
Set the following variables in your terminal shell session before executing:
* `PROJECT_ID`: Your target Google Cloud project ID (required).
* `REGION`: Target deployment region (defaults to `asia-south1`).
* `DB_INSTANCE`: Cloud SQL Instance identifier (defaults to `studymateai-db-instance`).
* `DB_NAME`: Database catalog identifier (defaults to `studymateai`).
* `SERVICE_NAME`: Cloud Run service wrapper identifier (defaults to `study-buddy-api`).
* `BUCKET_NAME`: Cloud Storage bucket identifier (defaults to `studymateai-curriculum-bucket`).
* `DB_PASSWORD`: Password for the root database user (`postgres`).

---

## Deployment Steps

### 1. Set Environment Variables
In your terminal, run:
```bash
export PROJECT_ID="your-gcp-project-id"
export DB_PASSWORD="your-secure-password"
```

### 2. Run Configuration Scripts Sequentially
Execute the shell files from the project root:

```bash
# Enable API endpoints (Vertex AI, Cloud SQL, Cloud Run, Firestore)
bash infra/gcloud/01-enable-apis.sh

# Create GCS Bucket for textbooks
bash infra/gcloud/02-create-bucket.sh

# Deploy Cloud SQL Postgres Database Instance (using db-f1-micro)
bash infra/gcloud/03-create-cloudsql.sh

# Configure Service Account Runner with minimal permissions (IAM)
bash infra/gcloud/04-create-service-account.sh

# Store database url inside Secret Manager
bash infra/gcloud/05-create-secrets.sh

# Build container and Deploy backend to Cloud Run
bash infra/gcloud/06-deploy-cloudrun.sh
```

---

## Free-Tier & Cost Boundary Constraints Enforced
- **Database Instance Tier**: Configured with `db-f1-micro` tier limits to fit within free or low-cost usage brackets.
- **Instances Bounds**: Configures Cloud Run with `min-instances=0` (scales to zero when idle) and `max-instances=2` (caps token scaling load costs).
- **Security Policies**: Uses Secret Manager to ensure no database credentials are hardcoded. Grants precise IAM roles (secretAccessor, datastore.user, storage.objectViewer, etc.) to the runner service account, adhering to minimal access policies.
