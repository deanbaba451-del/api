import os
import requests
import cv2
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Maksimum Koruma Aktif!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
TOKEN = '8694195722:AAETE-K-v1mDtTmmKAdLeX86iz-B9CA2r74' 
IMAGGA_KEY = 'acc_791d50abf6e9c95'
IMAGGA_SECRET = '6a39d107520cbde34f67a57f960599d0'

# Genişletilmiş Yasaklı Kelime ve Kategori Listesi
FORBIDDEN_KEYWORDS = {
    'weapon', 'gun', 'pistol', 'rifle', 'revolver', 'arm', 'firearm', 'knife', 'sword',
    'nudity', 'sex', 'porn', 'explicit', 'naked', 'underwear', 'lingerie', 'bikini', 
    'nude', 'breast', 'buttocks', 'erotic', 'pussy', 'penis', 'drug', 'narcotic', 'syringe',
    'blood', 'violence', 'gore', 'death'
}

# --- KOMUTLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # İstediğin özel mesaj
    await update.message.reply_text("Add me to your group")

# --- ANALİZ MANTIĞI ---
def is_content_forbidden(image_file):
    try:
        response = requests.post(
            'https://api.imagga.com/v2/tags',
            auth=(IMAGGA_KEY, IMAGGA_SECRET),
            files={'image': open(image_file, 'rb')},
            timeout=15
        )
        if response.status_code == 200:
            tags = response.json().get('result', {}).get('tags', [])
            for tag in tags:
                tag_name = tag['tag']['en'].lower()
                confidence = tag['confidence']
                
                # Çok düşük güven eşiği (%10) ile tüm riskli kelimeleri tara
                if confidence > 10 and any(word in tag_name for word in FORBIDDEN_KEYWORDS):
                    print(f"🛑 YASAKLI İÇERİK: {tag_name} (%{confidence})")
                    return True
    except Exception as e:
        print(f"API Hatası: {e}")
    return False

async def scan_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / (fps if fps > 0 else 25)
    
    # Videonun içine saklanmış kareleri bulmak için 8 farklı noktadan örnek alıyoruz
    check_points = [0.1, duration*0.2, duration*0.4, duration*0.5, duration*0.6, duration*0.8, duration-0.1]
    
    for p in check_points:
        if p < 0: continue
        cap.set(cv2.CAP_PROP_POS_MSEC, p * 1000)
        success, frame = cap.read()
        if success:
            tmp_name = f"v_scan_{p}.jpg"
            cv2.imwrite(tmp_name, frame)
            bad = is_content_forbidden(tmp_name)
            os.remove(tmp_name)
            if bad:
                cap.release()
                return True
    cap.release()
    return False

# --- ANA MOTOR ---
async def guard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message
    file_id = None
    is_video = False

    # Tüm medya tiplerini (Foto, Sticker, GIF, Video) yakala
    if msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.sticker:
        file_id = msg.sticker.file_id
    elif msg.animation or msg.video:
        file_id = (msg.animation or msg.video).file_id
        is_video = True
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith('image/'):
        file_id = msg.document.file_id

    if file_id:
        try:
            file = await context.bot.get_file(file_id)
            local_path = f"process_{file_id}"
            await file.download_to_drive(local_path)
            
            # Analiz et
            forbidden = await scan_video(local_path) if is_video else is_content_forbidden(local_path)
            os.remove(local_path)
            
            # Eğer yasaklıysa mesajı sil
            if forbidden:
                await msg.delete()
        except Exception as e:
            print(f"İşlem Hatası: {e}")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO | filters.Document.IMAGE, guard_handler))
    
    bot_app.run_polling()
