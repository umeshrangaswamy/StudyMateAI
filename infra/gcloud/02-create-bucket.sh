#!/bin/bash
# 02-create-bucket.sh - Create Cloud Storage bucket for grounding document files
set -e

PROJECT_ID=${PROJECT_ID}
REGION=${REGION:-asia-south1}
BUCKET_NAME=${BUCKET_NAME:-studymateai-curriculum-bucket}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    exit 1
fi

echo "Creating Cloud Storage bucket 'gs://$BUCKET_NAME' in location '$REGION'..."
gcloud storage buckets create "gs://$BUCKET_NAME" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --uniform-bucket-level-access

echo "GCP Cloud Storage bucket created successfully!"
