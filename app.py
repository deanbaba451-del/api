import os, telebot, io, time, imagehash
from flask import Flask, request
from PIL import Image

# --- BİLGİLERİN ---
TELEGRAM_TOKEN = "8694195722:AAGpxRjPNCpsdTYustm9n7ij2R3t6U_RoFg"
OWNER_ID = 6534222591 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

forbidden_hashes = {} 
forbidden_video_ids = set() 
authorized_users = {OWNER_ID} 

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "Sistem aktif sahip. Emirlerini bekliyorum.")
    else:
        bot.reply_to(message, "Beni grubuna ekle ve yetki ver!")

@bot.message_handler(func=lambda m: m.text and m.text.startswith(".auth") and m.chat.type == 'private')
def auth_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            new_id = int(message.text.split()[1]); authorized_users.add(new_id)
            bot.reply_to(message, f"✅ {new_id} yetkilendirildi.")
        except: bot.reply_to(message, "Hata! Örn: .auth 12345")

@bot.message_handler(content_types=['photo', 'video'])
def handle_media(message):
    user_id = message.from_user.id
    is_auth = user_id in authorized_users
    caption = message.caption or ""
    try:
        if message.content_type == 'video':
            v_id = message.video.file_id
            if is_auth and ("/yasakla" in caption or "/bulk" in caption):
                forbidden_video_ids.add(v_id); bot.reply_to(message, "✅ Video yasaklandı.")
                return
            if v_id in forbidden_video_ids:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, "Hasret ananizi siker")
        elif message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            img = Image.open(io.BytesIO(bot.download_file(bot.get_file(file_id).file_path)))
            current_hash = imagehash.phash(img)
            if is_auth and ("/yasakla" in caption or "/bulk" in caption):
                forbidden_hashes[current_hash] = file_id; bot.reply_to(message, "✅ Görsel yasaklandı.")
                return
            for f_hash in list(forbidden_hashes.keys()):
                if current_hash - f_hash < 5:
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.send_message(message.chat.id, "Hasret ananizi siker")
                    break
    except Exception as e: print(e)

@bot.message_handler(commands=['imagelist'])
def send_image_list(message):
    if message.from_user.id != OWNER_ID: return
    if not forbidden_hashes: bot.reply_to(message, "Liste boş."); return
    bot.reply_to(message, "Özelden atıyorum...");
    for f_hash, f_id in forbidden_hashes.items():
        bot.send_photo(OWNER_ID, f_id, caption="Yasaklı. Kaldırmak için reply .unban")
        time.sleep(0.5)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == ".unban")
def unban_media_handler(message):
    if message.from_user.id != OWNER_ID or not message.reply_to_message: return
    rep = message.reply_to_message
    try:
        if rep.content_type == 'video':
            v_id = rep.video.file_id
            if v_id in forbidden_video_ids: forbidden_video_ids.remove(v_id); bot.reply_to(message, "🔓 Kalktı.")
        elif rep.content_type == 'photo':
            img = Image.open(io.BytesIO(bot.download_file(bot.get_file(rep.photo[-1].file_id).file_path)))
            curr_hash = imagehash.phash(img); found = False
            for f_hash in list(forbidden_hashes.keys()):
                if curr_hash - f_hash < 5: del forbidden_hashes[f_hash]; found = True
            if found: bot.reply_to(message, "🔓 Kalktı.")
    except Exception as e: print(e)

# --- RENDER AYARLARI ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    # Önce environment'a bak, yoksa loglarındaki linki kullan
    url = os.getenv('RENDER_URL') or "https://api-1ywn.onrender.com"
    bot.set_webhook(url=f"{url}/{TELEGRAM_TOKEN}")
    return f"Sistem Hasret Adına Aktif! Link: {url}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
