# ---------- Stage 1: Build ----------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies only in build stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY report/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: Production ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY report /app

EXPOSE 5000

# Run Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]