# Sử dụng Python base image
FROM python:3.11-slim

WORKDIR /app

COPY dashboard /app

RUN pip install --no-cache-dir -r requirements.txt

COPY prometheus/targets.json /etc/prometheus/targets/targets.json
RUN chmod 666 /etc/prometheus/targets/targets.json

EXPOSE 8000

# Chạy ứng dụng Flask
CMD ["python", "main.py"]
