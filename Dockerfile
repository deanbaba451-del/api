# Python 3.9 hafif sürümünü kullanıyoruz
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Dosyaları kopyala
COPY . .

# Gerekli kütüphaneleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı başlat (Port Render tarafından otomatik atanır)
CMD ["python", "app.py"]
