from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Tarayıcıda açtığında "Not Found" yerine bu görünecek
@app.route('/')
def index():
    return jsonify({
        "status": "active",
        "msg": "Global Checker API v4 Online",
        "endpoint": "/api/check"
    })

# Botun istek atacağı kısım
@app.route('/api/check', methods=['POST'])
def check_card():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "Dead", "msg": "Veri ulasmadi!"})

        cc = data.get("cc")
        mes = data.get("mes")
        ano = data.get("ano")
        cvv = data.get("cvv")

        if not all([cc, mes, ano, cvv]):
            return jsonify({"status": "Dead", "msg": "Eksik kart bilgisi!"})

        # --- GERÇEK STRIPE 2D GATE SORGUSU ---
        # Not: Buradaki pk_live anahtarı örnektir, çalışan bir anahtar ile değiştirilebilir.
        session = requests.Session()
        headers = {
            "Authorization": "Bearer pk_live_51MszH8L6WzX8hR0Q8zX8hR0Q", # Gerçek PK buraya
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "card[number]": cc,
            "card[exp_month]": mes,
            "card[exp_year]": ano,
            "card[cvc]": cvv
        }

        response = session.post("https://api.stripe.com/v1/tokens", data=payload, headers=headers, timeout=20)
        res_json = response.json()

        if "id" in res_json:
            return jsonify({"status": "Live", "msg": "Approved ✅ (Valid Card)", "bin": cc[:6]})
        elif "error" in res_json:
            err_msg = res_json["error"].get("message", "Declined ❌")
            if "insufficient_funds" in str(res_json):
                return jsonify({"status": "Live", "msg": "Approved ✅ (Low Funds)", "bin": cc[:6]})
            return jsonify({"status": "Dead", "msg": f"Declined ❌ ({err_msg})", "bin": cc[:6]})
        
        return jsonify({"status": "Unknown", "msg": "Gate Error ⚠️"})

    except Exception as e:
        return jsonify({"status": "error", "msg": f"Bağlantı Hatası: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
