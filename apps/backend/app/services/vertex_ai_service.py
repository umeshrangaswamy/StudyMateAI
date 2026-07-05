import time
import logging
import os
import traceback
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Use the new google-genai SDK with Vertex AI backend
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("google-genai SDK not available. Using placeholder fallback.")


class VertexAIService:
    """
    Service wrapper for Google Cloud Vertex AI Gemini API.
    Uses the new google-genai async SDK with Vertex AI backend via ADC.
    Falls back gracefully to mock placeholder outputs if credentials/services are not active.
    """
    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.model_name = settings.MODEL_NAME
        self.client = None

        if GENAI_AVAILABLE:
            # In Cloud Run, credentials come automatically from attached service account.
            # In local dev, skip init if no ADC file found to avoid metadata server hangs.
            has_credentials = "GOOGLE_APPLICATION_CREDENTIALS" in os.environ

            if not has_credentials:
                if os.name == 'nt':
                    adc_path = os.path.expandvars("%APPDATA%\\gcloud\\application_default_credentials.json")
                else:
                    adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
                if os.path.exists(adc_path):
                    has_credentials = True

            if not has_credentials and settings.APP_ENV == "development":
                logger.warning("ADC not found locally. Skipping Vertex AI init.")
            else:
                try:
                    self.client = genai.Client(
                        vertexai=True,
                        project=self.project_id,
                        location=self.location,
                    )
                    logger.info(
                        f"VertexAIService initialized for GCP Project: {self.project_id}, "
                        f"Location: {self.location}, Model: {self.model_name}"
                    )
                except Exception as e:
                    logger.warning(f"Vertex AI client initialization failed: {str(e)}\n{traceback.format_exc()}")
        else:
            logger.info("Initializing VertexAIService in standalone placeholder mode.")

    async def generate_text(
        self,
        system_instruction: str,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generates text using the Gemini Model via google-genai async SDK.
        """
        start_time = time.time()
        limit_tokens = max_tokens if max_tokens is not None else settings.MAX_RESPONSE_TOKENS
        limit_tokens = min(limit_tokens, settings.MAX_RESPONSE_TOKENS)

        logger.info(
            f"Vertex AI Request -> Model: {self.model_name}, Temp: {temperature}, "
            f"MaxTokens: {limit_tokens}, PromptLength: {len(prompt)}"
        )

        if self.client is not None:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=limit_tokens,
                )
                # Use the native async client to avoid blocking the FastAPI event loop
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                latency = time.time() - start_time
                result_text = response.text
                logger.info(
                    f"Vertex AI Success -> Model: {self.model_name}, Latency: {latency:.3f}s, "
                    f"ResponseLength: {len(result_text) if result_text else 0}"
                )
                return result_text
            except Exception as e:
                latency = time.time() - start_time
                logger.error(
                    f"Vertex AI Generation Error -> Model: {self.model_name}, "
                    f"Latency: {latency:.3f}s, Error: {str(e)}\n{traceback.format_exc()}"
                )

        # Graceful placeholder fallback
        latency = time.time() - start_time
        logger.info(
            f"Vertex AI Mock Response -> Model: {self.model_name}, "
            f"Latency: {latency:.3f}s (Simulated)"
        )
        return (
            "[Vertex AI Placeholder Response]\n"
            "This is grounded text generated via Gemini Flash placeholder interface. "
            "It will synthesize curriculum context to output a simple, crisp, teacher-like explanation."
        )

    async def generate_json(
        self,
        system_instruction: str,
        prompt: str,
        schema: Any
    ) -> str:
        """
        Generates structured JSON output using Gemini structured output configuration.
        """
        start_time = time.time()
        logger.info(
            f"Vertex AI JSON Request -> Model: {self.model_name}, PromptLength: {len(prompt)}"
        )

        if self.client is not None:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.1,
                )
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                latency = time.time() - start_time
                logger.info(f"Vertex AI JSON Success -> Model: {self.model_name}, Latency: {latency:.3f}s")
                return response.text
            except Exception as e:
                latency = time.time() - start_time
                logger.error(
                    f"Vertex AI JSON Error -> Model: {self.model_name}, "
                    f"Latency: {latency:.3f}s, Error: {str(e)}\n{traceback.format_exc()}"
                )

        # Mock JSON response fallback
        latency = time.time() - start_time
        logger.info(
            f"Vertex AI Mock JSON Response -> Model: {self.model_name}, "
            f"Latency: {latency:.3f}s (Simulated)"
        )
        return '{"status": "mocked", "message": "GCP Vertex AI credentials not active"}'

    def estimate_tokens_if_possible(self, prompt: str) -> int:
        """
        Estimates the count of tokens for a given prompt query.
        """
        # Heuristic fallback (average 4 characters per token in English)
        return max(1, len(prompt) // 4)
