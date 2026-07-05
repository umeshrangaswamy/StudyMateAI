# Use official Python 3.11-slim base image for minimal footprint
FROM python:3.11-slim

# Set Python build and runtime settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Create a work directory
WORKDIR /app

# Install system dependencies (e.g. pg_config / gcc if build dependencies are needed, but psycopg2-binary doesn't strictly need them)
# Clean up apt caches to minimize layer size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy local packages and install them
COPY packages ./packages
RUN pip install --no-cache-dir -e ./packages/prompts

# Copy application source files
COPY . .

# Create a non-root security group and user to run the container safely
RUN groupadd -r appgroup && useradd -r -g appgroup appuser && \
    chown -R appuser:appgroup /app

# Switch executing context to the non-root user
USER appuser

# Expose target service port
EXPOSE 8080

# Run FastAPI application utilizing Uvicorn, dynamically binding the port from the environment
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
