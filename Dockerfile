FROM python:3.9-slim

WORKDIR /app

# Sistem kütüphanelerini güncelle
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render'da çalışması için portu Gunicorn'a bağlıyoruz
CMD gunicorn --bind 0.0.0.0:$PORT app:app
