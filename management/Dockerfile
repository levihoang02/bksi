FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY management /app

# Set proper permissions
RUN chown -R appuser:appuser /app

RUN chown -R 1000:1000 skeleton/
RUN chown -R 1000:1000 containers/

# Switch to non-root user
USER appuser

EXPOSE 3200

CMD ["python", "main.py"]
