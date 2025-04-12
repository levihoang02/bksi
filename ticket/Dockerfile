# Sử dụng Python base image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ticket /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# Chạy ứng dụng Flask
CMD ["python", "main.py"]
