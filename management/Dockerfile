FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY management/src /app/src
COPY management/modules /app/modules

# Set proper permissions
RUN chown -R appuser:appuser /app
RUN chmod -R 550 /app/src
RUN chmod -R 440 /app/modules

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3200/health || exit 1

CMD ["python", "src/app.py"]
