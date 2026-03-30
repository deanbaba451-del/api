FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Burada bot.py yerine app.py yazıyoruz:
CMD gunicorn --bind 0.0.0.0:$PORT app:app & python3 app.py
