#!/bin/bash
# 05-create-secrets.sh - Store sensitive DATABASE_URL connection keys in Secret Manager
set -e

PROJECT_ID=${PROJECT_ID}
REGION=${REGION:-asia-south1}
DB_INSTANCE=${DB_INSTANCE:-studymateai-db-instance}
DB_NAME=${DB_NAME:-studymateai}

# Provide DB Root password via DB_PASSWORD environment variable
DB_PASS=${DB_PASSWORD:-"YOUR_SECURE_PASSWORD_PLACEHOLDER"}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

# Formulate Unix socket postgres database connection layout path:
# postgresql://postgres:<password>@/studymateai?host=/cloudsql/<project_id>:<region>:<instance>
DB_URL="postgresql://postgres:$DB_PASS@/$DB_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE"

echo "Creating 'DATABASE_URL' secret inside Secret Manager..."
echo -n "$DB_URL" | gcloud secrets create DATABASE_URL \
    --data-file=- \
    --project="$PROJECT_ID" \
    --replication-policy="automatic"

echo "DATABASE_URL secret key successfully stored in Secret Manager!"
