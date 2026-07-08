$ErrorActionPreference = "Stop"

$PROJECT_ID = "project-2e926853-25a4-402b-a73"
$REGION = "asia-south1"
$SERVICE_NAME = "study-buddy-api"
$DB_INSTANCE = "studymateai-db-instance"
$BUCKET_NAME = "studymateai-data-2e926853"
$SA_NAME = "study-buddy-runner"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
$IMAGE_TAG = "asia-south1-docker.pkg.dev/$PROJECT_ID/studymateai-repo/${SERVICE_NAME}:latest"

Write-Host "============================================="
Write-Host "   StudyMateAI E2E GCP & Firebase Deployment  "
Write-Host "============================================="

Write-Host "=== Step 1: Configuring GCP Project ==="
gcloud config set project "$PROJECT_ID"

Write-Host "=== Step 2: Enabling GCP Services & APIs ==="
gcloud services enable run.googleapis.com sqladmin.googleapis.com firestore.googleapis.com aiplatform.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com

Write-Host "=== Step 3: Preparing Backend Build Context ==="
Write-Host "Copying local packages to backend source folder..."
if (Test-Path "apps/backend/packages") {
    Remove-Item -Recurse -Force "apps/backend/packages"
}
Copy-Item -Recurse -Force "packages" "apps/backend/packages"

Write-Host "=== Step 4: Submitting Container to Cloud Build ==="
gcloud builds submit --tag "$IMAGE_TAG" --project="$PROJECT_ID" ./apps/backend

Write-Host "=== Step 5: Deploying Backend to Cloud Run ==="
gcloud run deploy "$SERVICE_NAME" `
    --image="$IMAGE_TAG" `
    --region="$REGION" `
    --project="$PROJECT_ID" `
    --service-account="$SA_EMAIL" `
    --add-cloudsql-instances="${PROJECT_ID}:${REGION}:${DB_INSTANCE}" `
    --set-env-vars="APP_ENV=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,MODEL_NAME=gemini-2.5-flash-lite,EMBEDDING_MODEL=text-embedding-004,GOOGLE_GENAI_USE_VERTEXAI=true,GCS_KNOWLEDGE_BUCKET=$BUCKET_NAME" `
    --set-secrets="DATABASE_URL=DATABASE_URL:latest" `
    --min-instances=0 `
    --max-instances=2 `
    --allow-unauthenticated

Write-Host "=== Step 6: Compiling Frontend Next.js Static Site ==="
Push-Location apps/frontend
npm install
npm run build
Pop-Location

Write-Host "=== Step 7: Deploying Frontend to Firebase Hosting ==="
npx firebase deploy --only hosting

Write-Host "============================================="
Write-Host "   Deployment Completed Successfully!        "
Write-Host "============================================="
