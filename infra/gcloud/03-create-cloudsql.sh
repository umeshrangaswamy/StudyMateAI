#!/bin/bash
# 03-create-cloudsql.sh - Create Cloud SQL PostgreSQL db instance
set -e

PROJECT_ID=${PROJECT_ID}
REGION=${REGION:-asia-south1}
DB_INSTANCE=${DB_INSTANCE:-studymateai-db-instance}
DB_NAME=${DB_NAME:-studymateai}
DB_USER="postgres"

# SECURITY WARNING: DO NOT check in passwords to version control repositories.
# Provide database root password via DB_PASSWORD variable (defaults to placeholder instruction).
DB_PASS=${DB_PASSWORD:-"YOUR_SECURE_PASSWORD_PLACEHOLDER"}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

if [ "$DB_PASS" = "YOUR_SECURE_PASSWORD_PLACEHOLDER" ]; then
    echo "WARNING: Running setup script using password placeholder. Provide actual password via DB_PASSWORD."
    echo "Example: export DB_PASSWORD='my-safe-pass'"
fi

echo "Creating Cloud SQL PostgreSQL 15 Instance '$DB_INSTANCE' in location '$REGION'..."
echo "Configuring micro tier for low-cost MVP usage limits..."

gcloud sql instances create "$DB_INSTANCE" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --root-password="$DB_PASS"

echo "Creating Database catalog '$DB_NAME' inside Instance '$DB_INSTANCE'..."
gcloud sql databases create "$DB_NAME" \
    --instance="$DB_INSTANCE" \
    --project="$PROJECT_ID"

echo "Cloud SQL instance and Database created successfully!"
