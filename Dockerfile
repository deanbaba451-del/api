FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Render portu için değişkeni gunicorn'a paslıyoruz
CMD gunicorn --bind 0.0.0.0:$PORT app:app
