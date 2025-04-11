# Sử dụng Python base image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY report/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY healthcheck /app

EXPOSE 8001

CMD ["python", "main.py"]
