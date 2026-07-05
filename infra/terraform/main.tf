provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "studymateai-dev"
}

variable "region" {
  type        = string
  description = "GCP Region for deployment"
  default     = "us-central1"
}

# --- Cloud SQL PostgreSQL (Free Tier minimal size) ---
resource "google_sql_database_instance" "postgres" {
  name             = "studymateai-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Smallest available instance for free tier / dev cost optimization
    ip_configuration {
      ipv4_enabled = true
    }
  }
}

# --- Cloud SQL Database ---
resource "google_sql_database" "studymateai_db" {
  name     = "studymateai"
  instance = google_sql_database_instance.postgres.name
}

# --- Cloud Storage Bucket for Curriculum Documents ---
resource "google_storage_bucket" "knowledge_bucket" {
  name          = "${var.project_id}-knowledge-docs"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# --- Cloud Run Service for FastAPI Backend ---
resource "google_cloud_run_v2_service" "backend" {
  name     = "studymate-api"
  location = var.region

  template {
    scaling {
      min_instance_count = 0  # Crucial cost-control: scale to 0 when idle
      max_instance_count = 2  # Free Tier throttle constraint
    }

    containers {
      image = "gcr.io/${var.project_id}/studymate-api:latest"
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      env {
        name  = "STUDYMATEAI_APP_ENV"
        value = "production"
      }
      env {
        name  = "STUDYMATEAI_DATABASE_URL"
        value = "postgresql://postgres:postgres@localhost:5432/studymateai" # Update on post-deployment secrets injection
      }
    }
  }
}

# Output API service URL
output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "The URL of the deployed FastAPI Cloud Run service"
}
