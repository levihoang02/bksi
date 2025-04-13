# ---------- Stage 1: Build ----------
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY dashboard/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: Production ----------
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy service code
COPY dashboard /app

# Copy Prometheus config
COPY prometheus/targets.json /etc/prometheus/targets/targets.json
RUN chmod 666 /etc/prometheus/targets/targets.json

EXPOSE 8081

# Run Flask app directly (not using Gunicorn)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8081", "main:app"]
