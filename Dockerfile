# Hafif ve güncel bir Python imajı kullanıyoruz
FROM python:3.9-slim

# Sistem paketlerini güncelle ve OpenCV için gerekli kütüphaneleri yükle
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini oluştur
WORKDIR /app

# Önce gereksinimleri kopyala ve yükle (Cache avantajı için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Render'ın dinamik port yapısına uyum sağlamak ve 
# botu başlatmak için ana dosyayı çalıştır
CMD ["python", "app.py"]
