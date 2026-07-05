import logging
import sys
import json
import contextvars
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Thread and Async-safe ContextVars to store active request parameters
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
request_context_var: contextvars.ContextVar[dict] = contextvars.ContextVar("request_context", default={})

class JSONFormatter(logging.Formatter):
    """
    Formatter to output single-line JSON logs compatible with Google Cloud Logging.
    """
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage()
        }

        # Auto-inject ContextVars if populated
        req_id = request_id_var.get()
        if req_id:
            log_data["request_id"] = req_id

        req_ctx = request_context_var.get()
        if req_ctx:
            for k, v in req_ctx.items():
                log_data[k] = v

        # Extract extra properties supplied via logger.info("msg", extra={})
        standard_fields = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'message', 'module',
            'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
            'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        for key, value in record.__dict__.items():
            if key not in standard_fields:
                log_data[key] = value

        # Redact/Sanitize sensitive data (keys, passwords, full prompts, student PII)
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items() if not any(x in k.lower() for x in ["password", "key", "secret", "token", "credential", "auth"])}
            elif isinstance(obj, list):
                return [sanitize(x) for x in obj]
            elif isinstance(obj, str):
                if "AIzaSy" in obj:
                    return "[REDACTED_API_KEY]"
                if obj.startswith("Bearer "):
                    return "[REDACTED_BEARER_TOKEN]"
                if "You are Antigravity" in obj or "System Instructions:" in obj:
                    return "[REDACTED_SYSTEM_PROMPT]"
                return obj
            return obj

        return json.dumps(sanitize(log_data))

def setup_logging(log_level: str = "INFO"):
    """
    Configure root logger to use JSONFormatter, writing to standard output.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP Middleware assigning request_id context properties and tracking execution metrics.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Bind context variables
        token_id = request_id_var.set(request_id)
        token_ctx = request_context_var.set({})
        
        start_time = time.perf_counter()
        
        request_context_var.set({
            "method": request.method,
            "url_path": request.url.path,
        })
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger = logging.getLogger("app.middleware")
            logger.error(
                "Request failed with unhandled error",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise e
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger = logging.getLogger("app.middleware")
            logger.info(
                f"HTTP request processed in {duration_ms:.2f}ms",
                extra={
                    "latency_ms": duration_ms
                }
            )
            # Clean up context variables
            request_id_var.reset(token_id)
            request_context_var.reset(token_ctx)

