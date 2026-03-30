import os
import requests
import cv2
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- WEB SERVER (Render İçin) ---
app = Flask('')
@app.route('/')
def home(): return "Maksimum Hassasiyet Modu Aktif!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
# Yeni Token'ın buraya eklendi
TOKEN = '8694195722:AAETE-K-v1mDtTmmKAdLeX86iz-B9CA2r74' 
IMAGGA_KEY = 'acc_791d50abf6e9c95'
IMAGGA_SECRET = '6a39d107520cbde34f67a57f960599d0'

# GENİŞLETİLMİŞ YASAKLI LİSTESİ
FORBIDDEN = {
    'weapon', 'gun', 'pistol', 'rifle', 'revolver', 'arm', 'firearm', 'handgun', 'artillery', 'knife', 'dagger', 'sword',
    'nudity', 'sex', 'porn', 'explicit', 'naked', 'underwear', 'lingerie', 'bikini', 'nude', 'breast', 'buttocks', 'erotic',
    'drug', 'narcotic', 'syringe', 'cocaine', 'heroin', 'marijuana', 'cannabis', 'pill', 'tablet', 'capsule',
    'blood', 'violence', 'gore', 'injury', 'wound', 'dead'
}

# --- START KOMUTU ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sadece senin istediğin kısa mesajı gönderir
    await update.message.reply_text("Add me to your group")

# --- İÇERİK ANALİZİ ---
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
                tag_name = tag['tag']['en'].lower()
                confidence = tag['confidence']
                # Hassasiyet 15: En ufak benzerliği yakalar
                if confidence > 15 and tag_name in FORBIDDEN:
                    return True
    except:
        pass
    return False

async def scan_video_deep(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / (fps if fps > 0 else 25)
    
    # Videonun farklı noktalarından 6 kare alarak tarar
    check_points = [0.2, duration*0.2, duration*0.4, duration*0.6, duration*0.8, duration-0.2]
    
    for p in check_points:
        if p < 0: continue
        cap.set(cv2.CAP_PROP_POS_MSEC, p * 1000)
        success, frame = cap.read()
        if success:
            tmp_name = f"scan_{p}.jpg"
            cv2.imwrite(tmp_name, frame)
            is_bad = check_image(tmp_name)
            os.remove(tmp_name)
            if is_bad:
                cap.release()
                return True
    cap.release()
    return False

# --- ANA SESSİZ SİLİCİ ---
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
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith('image/'):
        file_id = msg.document.file_id

    if file_id:
        try:
            file = await context.bot.get_file(file_id)
            local_path = f"t_{file_id}"
            await file.download_to_drive(local_path)
            
            bad = await scan_video_deep(local_path) if is_video else check_image(local_path)
            os.remove(local_path)
            
            if bad:
                await msg.delete() # Sessizce siler
        except:
            pass

if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutlar
    bot_app.add_handler(CommandHandler("start", start))
    
    # Medya Filtreleme
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO | filters.Document.IMAGE, silent_guard))
    
    bot_app.run_polling()
