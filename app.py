import os
import telebot
from flask import Flask, request
from PIL import Image
import imagehash
import io

# --- AYARLARIN ---
TELEGRAM_TOKEN = "8694195722:AAGpxRjPNCpsdTYustm9n7ij2R3t6U_RoFg"
ADMIN_ID = 6534222591

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Hafızadaki yasaklı listeleri
forbidden_hashes = []
forbidden_video_ids = []

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    try:
        user_id = message.from_user.id
        is_admin = (user_id == ADMIN_ID)
        
        # Komutları kontrol et (Açıklama kısmında yazanlar)
        caption = message.caption if message.caption else ""
        is_bulk = "/bulk" in caption
        is_single = "/yasakla" in caption

        # 1. VİDEO İŞLEMLERİ
        if message.content_type == 'video':
            v_id = message.video.file_id
            
            # Yasaklama (Sadece Admin)
            if is_admin and (is_single or is_bulk):
                if v_id not in forbidden_video_ids:
                    forbidden_video_ids.append(v_id)
                    bot.reply_to(message, "✅ Video yasaklı listesine eklendi.")
                return

            # Yasaklı Video mu?
            if v_id in forbidden_video_ids:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, "Hasret ananizi siker")

        # 2. FOTOĞRAF İŞLEMLERİ
        elif message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            # Fotoğrafı bellekte analiz et
            img = Image.open(io.BytesIO(downloaded))
            current_hash = imagehash.phash(img)

            # Yasaklama (Sadece Admin)
            if is_admin and (is_single or is_bulk):
                if current_hash not in forbidden_hashes:
                    forbidden_hashes.append(current_hash)
                    bot.reply_to(message, "✅ Görsel yasaklı listesine eklendi.")
                return

            # Yasaklı Fotoğraf mı?
            for f_hash in forbidden_hashes:
                if current_hash - f_hash < 5: # Benzerlik toleransı
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, "Hasret ananizi siker")
                    break

    except Exception as e:
        print(f"Hata oluştu: {e}")

# --- RENDER WEBHOOK VE PORT YAPILANDIRMASI ---

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    """Telegram'dan gelen mesajları karşılar."""
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    """Web servisini aktif eder ve Webhook'u ayarlar."""
    bot.remove_webhook()
    # Render panelinden 'RENDER_URL' değerini alıyoruz (https://projeniz.onrender.com)
    render_url = os.getenv('RENDER_URL')
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TELEGRAM_TOKEN}")
        return "Bot Aktif ve Webhook Ayarlandı!", 200
    return "Hata: RENDER_URL ortam değişkeni tanımlı değil!", 400

if __name__ == "__main__":
    # Render'ın verdiği portu kullan, yoksa 5000 portunu kullan
    port = int(os.environ.get("PORT", 5000))
    # Flask sunucusunu başlat
    app.run(host="0.0.0.0", port=port)
