FROM python:3.10-slim

# install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# render port
EXPOSE 8080

CMD ["python", "app.py"]
