from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.endpoints import router as api_router
from app.core.logging import setup_logging, LoggingMiddleware

# Initialize logging framework
setup_logging(log_level=settings.LOG_LEVEL)

app = FastAPI(
    title="StudyMateAI Backend API",
    description="FastAPI backend shell for StudyMateAI serving SME agents and RAG (MVP)",
    version="1.0.0",
)

# Set up logging middleware first to intercept request context and generate request IDs
app.add_middleware(LoggingMiddleware)

# Set up CORS middleware for local testing and hosting connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origin constraints for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom validation exception handler for clean, student-friendly error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        message = error.get("msg", "Validation error")
        # Strip generic Pydantic default prefix for cleaner details
        if message.startswith("Value error, "):
            message = message.replace("Value error, ", "")
        error_messages.append(message)
        
    return JSONResponse(
        status_code=400,
        content={"detail": "; ".join(error_messages)}
    )

# Include router containing health, ready, and ask endpoints
app.include_router(api_router)
