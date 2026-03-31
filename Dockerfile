FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Dosyaları kopyala
COPY . .

# Gerekli kütüphaneleri kur
RUN pip install --no-cache-dir -r requirements.txt

# Botu başlat
CMD ["python", "kudur.py"]
