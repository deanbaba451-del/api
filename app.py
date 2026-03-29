import os
import random
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- PROFESYONEL ARAÇLAR ---
def luhn_check(card_no):
    """Kart numarasının matematiksel geçerliliğini kontrol eder."""
    try:
        digits = [int(d) for d in str(card_no)]
        checksum = sum(digits[-1::-2])
        for d in digits[-2::-2]:
            checksum += sum(divmod(d * 2, 10))
        return checksum % 10 == 0
    except:
        return False

def get_bank_info(cc):
    """BIN (ilk 6 hane) üzerinden sahte banka ve tip bilgisi üretir."""
    bin_6 = str(cc)[:6]
    types = ["PLATINUM", "GOLD", "BUSINESS", "CLASSIC", "INFINITE"]
    banks = ["ZIRAAT", "GARANTI", "YAPI KREDI", "AKBANK", "IS BANKASI"]
    
    # Gerçekçi görünmesi için BIN'e göre sabit ama rastgele seçim
    random.seed(bin_6)
    return {
        "bank": random.choice(banks),
        "level": random.choice(types),
        "brand": "VISA" if cc.startswith("4") else "MASTERCARD" if cc.startswith("5") else "AMEX"
    }

# --- ROTALAR ---
@app.route('/')
def live():
    # Cron Job burayı tetikleyecek
    return jsonify({"status": "live", "uptime": "24/7", "author": "Mert"}), 200

@app.route('/api/calculate', methods=['POST'])
def calculate_points():
    start_time = time.time()
    data = request.get_json()
    
    if not data or 'card_number' not in data:
        return jsonify({"status": "fail", "msg": "Input Error: Card number required"}), 400

    card_no = str(data['card_number']).replace(" ", "").replace("-", "")

    # 1. Luhn Kontrolü (Gerçekçilik Katmanı)
    if not luhn_check(card_no) or len(card_no) < 15:
        return jsonify({
            "status": "declined",
            "msg": "Luhn Check Failed: Invalid Card Number",
            "code": "L01"
        }), 200

    # 2. Banka ve Kart Bilgisi
    info = get_bank_info(card_no)
    
    # 3. Puan Hesaplama (Rastgele ama Mantıklı)
    # Kartın son hanesine göre 500-5000 arası puan üretir
    random.seed(card_no[-4:]) 
    points = random.randint(500, 5000)

    execution_time = round(time.time() - start_time, 4)

    return jsonify({
        "status": "success",
        "data": {
            "card_display": f"{card_no[:6]}******{card_no[-4:]}",
            "bank": info['bank'],
            "level": info['level'],
            "brand": info['brand'],
            "calculated_points": points,
            "currency": "BONUS Puan"
        },
        "performance": f"{execution_time}s",
        "msg": "API Response: Calculation Successful"
    }), 200

if __name__ == "__main__":
    # Render Port ve Host ayarı
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
