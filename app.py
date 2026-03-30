import os
import requests
import cv2
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- WEB SERVER (Render/Cron İçin) ---
app = Flask('')
@app.route('/')
def home(): return "Sessiz Gardiyan Aktif!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
TOKEN = '8694195722:AAHhRsI_LVBbR71L3J6Db4xwfuAij27zCK4' 
IMAGGA_KEY = 'acc_791d50abf6e9c95'
IMAGGA_SECRET = '6a39d107520cbde34f67a57f960599d0'

# Yasaklı Listesi
FORBIDDEN = {'weapon', 'gun', 'drug', 'narcotic', 'pistol', 'syringe', 'nudity', 'sex', 'porn', 'blood'}

# --- İÇERİK ANALİZ MOTORU ---
def check_image(image_file):
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
                if tag['confidence'] > 35 and tag['tag']['en'].lower() in FORBIDDEN:
                    return True
    except:
        pass
    return False

# --- VİDEO DERİN TARAMA ---
async def scan_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / (fps if fps > 0 else 25)

    # Baş, orta, son kareleri kontrol et
    points = [1, duration / 2, duration - 1] if duration > 3 else [1]
    
    for p in points:
        cap.set(cv2.CAP_PROP_POS_MSEC, p * 1000)
        success, frame = cap.read()
        if success:
            tmp_frame = f"f_{p}.jpg"
            cv2.imwrite(tmp_frame, frame)
            bad = check_image(tmp_frame)
            os.remove(tmp_frame)
            if bad:
                cap.release()
                return True
    cap.release()
    return False

# --- ANA SESSİZ YÖNETİCİ ---
async def silent_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    
    msg = update.message
    file_id = None
    is_video = False

    if msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.sticker:
        file_id = msg.sticker.file_id
    elif msg.animation or msg.video:
        file_id = (msg.animation or msg.video).file_id
        is_video = True

    if file_id:
        file = await context.bot.get_file(file_id)
        local_path = f"tmp_{file_id}"
        await file.download_to_drive(local_path)

        # Analiz Et
        bad = await scan_video(local_path) if is_video else check_image(local_path)
        
        os.remove(local_path)

        # Yasaklıysa Sessizce Sil
        if bad:
            try:
                await msg.delete()
            except:
                pass # Yetki hatası vb. olursa bot çökmesin

if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    # Tüm medyaları dinle, hiçbir komut veya yazı yazma
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO, silent_guard))
    
    print("Sessiz İmha Modu Aktif. Bot hiçbir mesaj atmayacak.")
    bot_app.run_polling()
