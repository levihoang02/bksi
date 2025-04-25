# ---------- Stage 1: Build ----------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies only for this stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements into a temporary install location
COPY healthcheck/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: Production ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy the application code
COPY healthcheck /app

EXPOSE 8001

# Run the application
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8001", "main:app"]