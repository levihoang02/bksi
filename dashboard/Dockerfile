# Sử dụng Python base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ thư mục dashboard vào container
COPY dashboard /app

COPY kafka_utils /app/kafka_utils

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

COPY prometheus/targets.json /etc/prometheus/targets/targets.json
RUN chmod 666 /etc/prometheus/targets/targets.json

# Expose cổng 8000 cho Flask API
EXPOSE 8000

# Chạy ứng dụng Flask
CMD ["python", "main.py"]
