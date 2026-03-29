import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ÖNEMLİ: Bu URL, seçtiğin sistemin (Bursakart/Setcard vb.) API ucudur.
# Şimdilik genel bir yapı kurdum, siteyi netleştirdiğimizde tam adresi buraya yazarız.
TARGET_SYSTEM_URL = "https://api.bursakart.com.tr/v1/card/balance" 

@app.route('/')
def check_status():
    return jsonify({"status": "online", "message": "7/24 Gercek Bakiye API"}), 200

@app.route('/api/sorgula', methods=['POST'])
def bakiye_sorgula():
    data = request.get_json()
    card_no = str(data.get('card_number', '')).replace(" ", "")

    if len(card_no) < 10:
        return jsonify({"error": "Gecersiz kart numarasi"}), 400

    # SİTEYE GERÇEK İSTEK ATMA BÖLÜMÜ
    payload = {"alias": card_no} # Site hangi parametreyi istiyorsa (alias/cardNo)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
        "Content-Type": "application/json",
        "Referer": "https://www.bursakart.com.tr/"
    }

    try:
        # Gerçek sisteme bağlanıyoruz
        response = requests.post(TARGET_SYSTEM_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_data = response.json()
            # Siteden gelen gerçek rakamı yakalıyoruz
            # Not: 'balance' ismi siteden siteye değişebilir (tutar, bakiye vb.)
            real_balance = res_data.get("data", {}).get("balance", "0.00")
            
            return jsonify({
                "status": "success",
                "card": card_no,
                "bakiye": f"{real_balance} TL",
                "msg": "Gercek veri sistemden cekildi."
            }), 200
        else:
            return jsonify({"status": "error", "msg": "Sistemden cevap alinamadi"}), 500

    except Exception as e:
        return jsonify({"status": "error", "msg": "Baglanti hatasi", "detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
