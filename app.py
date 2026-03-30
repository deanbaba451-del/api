import os
import telebot
from flask import Flask, request
from PIL import Image
import imagehash
import io

# --- BİLGİLERİN ---
TELEGRAM_TOKEN = "8694195722:AAGpxRjPNCpsdTYustm9n7ij2R3t6U_RoFg"
ADMIN_ID = 6534222591

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Yasaklı listeleri
forbidden_hashes = []
forbidden_video_ids = []

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    try:
        user_id = message.from_user.id
        is_admin = (user_id == ADMIN_ID)
        
        # Komut kontrolü (Tekli yasakla veya Bulk yasakla)
        is_bulk = message.caption and "/bulk" in message.caption
        is_single = message.caption and "/yasakla" in message.caption

        # 1. VİDEO İŞLEMLERİ
        if message.content_type == 'video':
            v_id = message.video.file_id
            
            if is_admin and (is_single or is_bulk):
                if v_id not in forbidden_video_ids:
                    forbidden_video_ids.append(v_id)
                    bot.reply_to(message, "✅ Video bulk listesine eklendi.")
                return

            # Yasaklı Video mu?
            if v_id in forbidden_video_ids:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, "Hasret ananizi siker")

        # 2. FOTOĞRAF İŞLEMLERİ
        elif message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            img = Image.open(io.BytesIO(downloaded))
            current_hash = imagehash.phash(img)

            if is_admin and (is_single or is_bulk):
                if current_hash not in forbidden_hashes:
                    forbidden_hashes.append(current_hash)
                    bot.reply_to(message, "✅ Görsel bulk listesine eklendi.")
                return

            # Yasaklı Fotoğraf mı?
            for f_hash in forbidden_hashes:
                if current_hash - f_hash < 5:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, "Hasret ananizi siker")
                    break

    except Exception as e:
        print(f"Hata: {e}")

# --- RENDER/FLASK AYARLARI ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    render_url = os.getenv('RENDER_URL')
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TELEGRAM_TOKEN}")
        return "Hasret'in Bulk Botu Aktif!", 200
    return "RENDER_URL Eksik!", 400

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
