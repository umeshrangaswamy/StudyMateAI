from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # GCP Configs
    GOOGLE_CLOUD_PROJECT: str = "studymateai-dev"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_GENAI_USE_VERTEXAI: bool = True

    # Cloud SQL PostgreSQL Configs
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/studymateai"

    # Google Cloud Storage Configs
    GCS_KNOWLEDGE_BUCKET: str = "studymateai-knowledge-docs"

    # Gemini Configs
    MODEL_NAME: str = "gemini-2.5-flash-lite"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    # App Configs
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Cost Controls & MVP Boundaries Configs
    MAX_RAG_CHUNKS: int = 3
    MAX_RESPONSE_TOKENS: int = 2048
    ENABLE_INTERNET_AGENT: bool = False
    ENABLE_PERSONALIZATION: bool = False

    # Properties mapping backward compatibility
    @property
    def GCP_PROJECT_ID(self) -> str:
        return self.GOOGLE_CLOUD_PROJECT

    @property
    def GCP_LOCATION(self) -> str:
        return self.GOOGLE_CLOUD_LOCATION

    @property
    def GEMINI_MODEL_NAME(self) -> str:
        return self.MODEL_NAME

    @property
    def EMBEDDING_MODEL_NAME(self) -> str:
        return self.EMBEDDING_MODEL

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
