FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask gunicorn requests
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app:app"]
