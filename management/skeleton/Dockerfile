# Sử dụng Python base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ thư mục dashboard vào container
COPY . /app

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Expose cổng 8000 cho Flask API
EXPOSE 8120

# Chạy ứng dụng Flask
CMD ["python", "main.py"]
