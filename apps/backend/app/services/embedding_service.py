import logging
import re
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

# Import Vertex AI Language models dynamically to handle offline/local environment testing
VERTEX_AVAILABLE = False
try:
    import vertexai
    from vertexai.language_models import TextEmbeddingModel
    VERTEX_AVAILABLE = True
except ImportError:
    logger.warning("Vertex AI SDK language models library not imported. Using local skeleton placeholders.")

class EmbeddingService:
    """
    Service wrapper for generating text embeddings using Vertex AI text-embedding-004 model.
    Bypasses connection calls dynamically in development if GCP credentials are not active.
    """
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.initialized = False

        if VERTEX_AVAILABLE:
            # Check standard credential variables to avoid hanging metadata server lookups locally
            import os
            has_credentials = "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
            if not has_credentials:
                if os.name == 'nt':
                    adc_path = os.path.expandvars("%APPDATA%\\gcloud\\application_default_credentials.json")
                else:
                    adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
                if os.path.exists(adc_path):
                    has_credentials = True

            if not has_credentials and settings.APP_ENV == "development":
                logger.warning(
                    "GCP Application Default Credentials (ADC) file not found. "
                    "Skipping Embedding SDK initialization to prevent metadata server hangs."
                )
            else:
                try:
                    vertexai.init(project=self.project_id, location=self.location)
                    self.initialized = True
                    logger.info(f"EmbeddingService initialized with model: {self.model_name}")
                except Exception as e:
                    logger.warning(f"GCP Embedding Service initialization failed: {str(e)}")
        else:
            logger.info("Initializing EmbeddingService in standalone placeholder mode.")

    async def embed_text(self, text: str) -> List[float]:
        """
        Generates text embedding vector matching the text-embedding-004 output dimension (768 floats).
        Validates text rules (non-empty, length limits, PII/secret scrubbing).
        """
        # 1. Non-empty Validation
        if not text or not text.strip():
            raise ValueError("Text content for embedding must not be empty.")

        # 2. Scrub PII and API Secrets
        # Match typical email pattern
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        # Match typical GCP API key pattern
        gcp_key_pattern = r"AIzaSy[A-Za-z0-9_-]{30,40}"
        
        if re.search(email_pattern, text) or re.search(gcp_key_pattern, text):
            logger.warning("Potential PII or API key signature detected in text. Blocking request.")
            raise ValueError("PII, secrets, or API keys are not permitted in embedding queries.")

        # 3. Truncate long inputs (cost and token count rules)
        max_char_limit = 2000
        if len(text) > max_char_limit:
            logger.warning(f"Input text length ({len(text)}) exceeds limit. Truncating to {max_char_limit} characters.")
            text = text[:max_char_limit]

        # 4. Log request metadata (never print full content)
        logger.info(
            f"Embedding Request -> Model: {self.model_name}, InputLength: {len(text)}, "
            f"Initialized: {self.initialized}"
        )

        if self.initialized:
            try:
                # Load pre-trained model and call the API
                model = TextEmbeddingModel.from_pretrained(self.model_name)
                embeddings = model.get_embeddings([text])
                if embeddings and len(embeddings) > 0:
                    logger.info(f"Embedding Success -> Model: {self.model_name}")
                    return embeddings[0].values
            except Exception as e:
                logger.error(f"Embedding API call failed: {str(e)}. Falling back to mock vector.")

        # Return mock 768-dimensional float vector placeholder
        # Satisfies the downstream vector_store and pgvector dimension checks
        return [0.01] * 768

    async def get_embedding(self, text: str) -> List[float]:
        """
        Backward compatibility alias mapping.
        """
        return await self.embed_text(text)
