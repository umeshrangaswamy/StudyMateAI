#!/bin/bash
# 06-deploy-cloudrun.sh - Build container using Cloud Build and deploy to Cloud Run
set -e

PROJECT_ID=${PROJECT_ID}
REGION=${REGION:-asia-south1}
SERVICE_NAME=${SERVICE_NAME:-study-buddy-api}
DB_INSTANCE=${DB_INSTANCE:-studymateai-db-instance}
BUCKET_NAME=${BUCKET_NAME:-studymateai-data-2e926853}
SA_NAME="study-buddy-runner"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

IMAGE_TAG="asia-south1-docker.pkg.dev/$PROJECT_ID/studymateai-repo/$SERVICE_NAME:latest"

# Get base project directory to locate Dockerfile / backend source files
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(dirname "$(dirname "$SCRIPT_DIR")")
BACKEND_SRC="$PROJECT_ROOT/apps/backend"

# Ensure local packages folder is copied into backend build context
echo "Copying local packages to backend source folder..."
cp -r "$PROJECT_ROOT/packages" "$BACKEND_SRC/"

echo "Building and registering Docker container image using Cloud Build..."
gcloud builds submit --tag "$IMAGE_TAG" --project="$PROJECT_ID" "$BACKEND_SRC"

echo "Deploying container image to Cloud Run service '$SERVICE_NAME' in region '$REGION'..."
echo "Setting min instances=0 and max instances=2 for MVP cost limitations..."

gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SA_EMAIL" \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:$DB_INSTANCE" \
    --set-env-vars="APP_ENV=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,MODEL_NAME=gemini-2.5-flash-lite,EMBEDDING_MODEL=text-embedding-004,GOOGLE_GENAI_USE_VERTEXAI=true,GCS_KNOWLEDGE_BUCKET=$BUCKET_NAME" \
    --set-secrets="DATABASE_URL=DATABASE_URL:latest" \
    --min-instances=0 \
    --max-instances=2 \
    --allow-unauthenticated

echo "Cloud Run API Service successfully deployed!"
