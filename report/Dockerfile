# Sử dụng Python 3.9 làm base image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY report/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY report /app

EXPOSE 5000

CMD ["python", "main.py"]