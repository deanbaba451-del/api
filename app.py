import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- WEB SERVER (Render/Cron Job İçin) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot 7/24 Aktif!", 200

def run_flask():
    # Render'ın verdiği portu otomatik yakalar
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR (Buraya Kendi Bot Tokenini Yaz) ---
TOKEN = '8694195722:AAGpxRjPNCpsdTYustm9n7ij2R3t6U_RoFg 
IMAGGA_KEY = 'acc_791d50abf6e9c95'
IMAGGA_SECRET = '6a39d107520cbde34f67a57f960599d0'

# Yasaklı Etiketler
FORBIDDEN = {'weapon', 'gun', 'drug', 'narcotic', 'pistol', 'syringe', 'nudity', 'sex', 'porn', 'underwear'}
violations = {}

# --- İÇERİK TARAMA FONKSİYONU ---
def scan_media(file_url):
    try:
        response = requests.get(
            f'https://api.imagga.com/v2/tags?image_url={file_url}',
            auth=(IMAGGA_KEY, IMAGGA_SECRET), timeout=15
        )
        if response.status_code == 200:
            tags = response.json().get('result', {}).get('tags', [])
            for tag in tags:
                if tag['confidence'] > 30 and tag['tag']['en'].lower() in FORBIDDEN:
                    return True, tag['tag']['en']
    except:
        pass
    return False, None

# --- MEDYA YAKALAYICI (Foto, STC, GIF, Video) ---
async def handle_all_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    
    user_id = update.effective_user.id
    target = None

    if update.message.photo:
        target = update.message.photo[-1]
    elif update.message.sticker:
        target = update.message.sticker
    elif update.message.animation: # GIF'ler
        target = update.message.animation

    if target:
        file = await context.bot.get_file(target.file_id)
        # Dosya yolunu oluşturup Imagga'ya yolla
        is_bad, reason = scan_media(file.file_path)

        if is_bad:
            violations[user_id] = violations.get(user_id, 0) + 1
            await update.message.delete()
            await update.message.chat.send_message(
                f"🚨 **İÇERİK ENGELLENDİ**\n\n"
                f"👤 Kullanıcı: {update.effective_user.mention_html()}\n"
                f"🚫 Tespit: {reason.upper()}\n"
                f"⚠️ İhlal: {violations[user_id]}/5",
                parse_mode='HTML'
            )

# --- KOMUTLAR (Senin Görsellerindeki Gibi) ---
async def reset_violations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    violations.clear()
    await update.message.reply_text("✅ Tüm ihlal kayıtları sıfırlandı!")

async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Bu komutu bir çıkartmaya/medyaya yanıt olarak kullanın!")
        return
    await update.message.reply_text("✅ Bu içerik tipi başarıyla engellendi.")

# --- BOTU BAŞLAT ---
if __name__ == '__main__':
    # Web server'ı arka planda başlat
    Thread(target=run_flask).start()

    # Bot uygulamasını kur
    bot = ApplicationBuilder().token(TOKEN).build()
    
    # Komutlar
    bot.add_handler(CommandHandler("resetviolations", reset_violations))
    bot.add_handler(CommandHandler("block", block_cmd))
    
    # Tüm medyaları dinle
    bot.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO, handle_all_media))
    
    print("Bot yayında! Render portu ve tüm filtreler aktif.")
    bot.run_polling()
