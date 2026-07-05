#!/bin/bash
# 04-create-service-account.sh - Create service runner account with minimal privileges
set -e

PROJECT_ID=${PROJECT_ID}
SA_NAME="study-buddy-runner"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

echo "Creating dedicated IAM Service Account '$SA_NAME' in project '$PROJECT_ID'..."
gcloud iam service-accounts create "$SA_NAME" \
    --description="Execution runner for StudyMateAI Cloud Run app service" \
    --display-name="StudyMateAI Cloud Run Runner" \
    --project="$PROJECT_ID"

echo "Binding IAM permissions (Secret Manager Access, Vertex AI user, Cloud SQL client, Storage reader, Firestore user)..."

# Secret Manager secretAccessor
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Vertex AI user
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

# Cloud SQL client
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudsql.client"

# Firestore/Datastore User
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/datastore.user"

# Cloud Storage Reader
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectViewer"

echo "Dedicated runner Service Account created and configured successfully!"
