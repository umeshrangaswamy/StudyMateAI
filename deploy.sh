#!/bin/bash
# deploy.sh - Unified E2E GCP & Firebase Deployment Script
set -e

PROJECT_ID="project-2e926853-25a4-402b-a73"
REGION="asia-south1"
SERVICE_NAME="study-buddy-api"
DB_INSTANCE="studymateai-db-instance"
BUCKET_NAME="studymateai-data-2e926853"
SA_NAME="study-buddy-runner"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
IMAGE_TAG="asia-south1-docker.pkg.dev/$PROJECT_ID/studymateai-repo/$SERVICE_NAME:latest"

echo "============================================="
echo "   StudyMateAI E2E GCP & Firebase Deployment  "
echo "============================================="

echo "=== Step 1: Configuring GCP Project ==="
gcloud config set project "$PROJECT_ID"

echo "=== Step 2: Enabling GCP Services & APIs ==="
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com

echo "=== Step 3: Preparing Backend Build Context ==="
echo "Copying local packages to backend source folder..."
cp -r ./packages ./apps/backend/

echo "=== Step 4: Submitting Container to Cloud Build ==="
gcloud builds submit --tag "$IMAGE_TAG" --project="$PROJECT_ID" ./apps/backend

echo "=== Step 5: Deploying Backend to Cloud Run ==="
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

echo "=== Step 6: Compiling Frontend Next.js Static Site ==="
cd apps/frontend
npm install
npm run build
cd ../..

echo "=== Step 7: Deploying Frontend to Firebase Hosting ==="
npx firebase deploy --only hosting

echo "============================================="
echo "   Deployment Completed Successfully!        "
echo "============================================="
echo "Backend API Service: https://study-buddy-api-47964766521.asia-south1.run.app"
echo "Frontend Hosting:    https://project-2e926853-25a4-402b-a73.web.app"
echo "============================================="
