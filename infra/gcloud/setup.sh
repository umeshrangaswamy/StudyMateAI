#!/bin/bash
# StudyMateAI GCP Initialization & Setup script

set -e

PROJECT_ID="project-2e926853-25a4-402b-a73"
REGION="asia-south1"

echo "1. Setting active project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "2. Enabling necessary API services..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com

echo "3. Creating Cloud Storage bucket for Terraform state (optional)..."
# gsutil mb -l "$REGION" "gs://$PROJECT_ID-tfstate" || true

echo "4. Ready! Execute terraform init & apply within infra/terraform/ folder to proceed."
