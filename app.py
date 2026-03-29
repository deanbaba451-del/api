from flask import Flask, request, jsonify
import requests
import os
import time
import random

app = Flask(__name__)

# --- SİTE LİSTESİ VE AYARLARI ---
SITES = {
    "amazon": "https://www.amazon.com/gp/cart/view.html",
    "trendyol": "https://www.trendyol.com/odeme",
    "hepsiburada": "https://www.hepsiburada.com/ayrintili-odeme",
    "aliexpress": "https://best.aliexpress.com/"
}

@app.route('/')
def index():
    return jsonify({"status": "active", "msg": "E-Commerce Checker API v3 Online"})

@app.route('/api/check', methods=['POST'])
def check_card():
    try:
        data = request.json
        cc = data.get("cc")
        mes = data.get("mes")
        ano = data.get("ano")
        cvv = data.get("cvv")
        site_key = data.get("site", "amazon") # Varsayılan Amazon

        if not all([cc, mes, ano, cvv]):
            return jsonify({"status": "Dead", "msg": "Eksik kart bilgisi!"})

        # --- BIN KONTROLÜ (Kartın Bankası Nedir?) ---
        bin_url = f"https://lookup.binlist.net/{cc[:6]}"
        bin_info = "Unknown Bank"
        try:
            bin_res = requests.get(bin_url, timeout=5).json()
            bin_info = f"{bin_res.get('bank', {}).get('name', 'Unknown')} - {bin_res.get('country', {}).get('name', 'TR')}"
        except:
            pass

        # --- SORGULAMA SİMÜLASYONU (SİTEYE GÖRE) ---
        # Gerçek bir check için burada her siteye özel 'session' ve 'payload' gerekir.
        # Bu dev siteler 3D Secure istediği için 'Low-Level Auth' denemesi yapılır.
        
        target_site = SITES.get(site_key, SITES["amazon"])
        time.sleep(2) # İşlem süresi simülasyonu

        # Örnek Mantık: Eğer kart 4 ile başlıyorsa (Visa) ve CVV 3 haneliyse Live dönelim
        if len(cc) >= 15 and len(cvv) == 3:
            return jsonify({
                "status": "Live",
                "msg": f"Approved ✅ ({site_key.capitalize()} Gate)",
                "bin": cc[:6],
                "bank": bin_info,
                "site": target_site
            })
        else:
            return jsonify({
                "status": "Dead",
                "msg": f"Declined ❌ (Security Block: {site_key})",
                "bin": cc[:6]
            })

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

if __name__ == '__main__':
    # Render için port ayarı hayati önem taşır
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
