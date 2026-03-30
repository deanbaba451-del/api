from python:3.9-slim

# sistem paketlerini güncelle ve opencv bağımlılıklarını yükle
run apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

workdir /app

copy requirements.txt .
run pip install --no-cache-dir -r requirements.txt

copy . .

cmd ["python", "app.py"]
