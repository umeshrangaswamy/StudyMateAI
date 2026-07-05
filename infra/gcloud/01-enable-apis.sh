#!/bin/bash
# 01-enable-apis.sh - Enable all required Google Cloud Service APIs
set -e

# Enforce active project ID
if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set."
    echo "Please set it before running: export PROJECT_ID='your-project-id'"
    exit 1
fi

echo "Configuring active GCP project context: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "Enabling GCP Resource Service APIs..."
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com

echo "All required GCP Service APIs enabled successfully!"
