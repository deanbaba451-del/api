import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Bursakart Gerçek API Adresi
BURSAKART_API = "https://api.burulas.com.tr/v1/card/balance"

@app.route('/')
def health():
    return jsonify({"status": "active", "msg": "Bursakart Real-Time API"}), 200

@app.route('/api/sorgula', methods=['POST'])
def bakiye_cek():
    data = request.get_json()
    card_no = str(data.get('card_number', '')).strip()

    if len(card_no) < 10:
        return jsonify({"status": "fail", "msg": "Gecersiz Kart Numarasi"}), 400

    # Gerçek Sisteme Gönderilecek Veri
    payload = {"alias": card_no}
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Content-Type": "application/json",
        "Origin": "https://www.bursakart.com.tr",
        "Referer": "https://www.bursakart.com.tr/"
    }

    try:
        # Gerçek Bursakart sistemine bağlanıyoruz
        response = requests.post(BURSAKART_API, json=payload, headers=headers, timeout=12)
        
        if response.status_code == 200:
            res_json = response.json()
            # Sistemden gelen gerçek veri
            # Bursakart genellikle 'data' içindeki 'balance' alanını kullanır
            bakiye = res_json.get("data", {}).get("balance", "0.00")
            
            return jsonify({
                "status": "success",
                "card": card_no,
                "bakiye": f"{bakiye} TL",
                "system": "Bursakart Official"
            }), 200
        else:
            return jsonify({"status": "fail", "msg": "Sistem su an cevap vermiyor"}), 500

    except Exception as e:
        return jsonify({"status": "error", "msg": "Baglanti hatasi olustu"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
