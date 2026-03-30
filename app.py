import os
import requests
import cv2
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- web server (render için) ---
app = Flask('')
@app.route('/')
def home(): return "sightengine guard aktif!", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- ayarlar ---
token = '8694195722:AAETE-K-v1mDtTmmKAdLeX86iz-B9CA2r74'
sightengine_user = '1773861365'
sightengine_secret = 'j7Hjr6oa4CLWrPTXZfEUaujCeh4o4p6e'

# --- start komutu ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # reply atmadan düz mesaj yazar ve küçük harf kullanır
    await context.bot.send_message(chat_id=update.effective_chat.id, text="add me to your group")

# --- sightengine analiz motoru ---
def check_content(image_path):
    params = {
        'models': 'nudity-2.1,weapon,drugs,gore',
        'api_user': sightengine_user,
        'api_secret': sightengine_secret
    }
    files = {'media': open(image_path, 'rb')}
    
    try:
        response = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
        output = response.json()
        
        if output['status'] == 'success':
            # çıplaklık, silah, uyuşturucu veya kan varsa %10 ihtimal bile olsa siler
            is_nudity = any(output.get('nudity', {}).get(k, 0) > 0.1 for k in ['sexual_activity', 'sexual_display', 'erotica'])
            is_weapon = output.get('weapon', 0) > 0.1
            is_drugs = output.get('drugs', 0) > 0.1
            is_gore = output.get('gore', {}).get('prob', 0) > 0.1
            
            if is_nudity or is_weapon or is_drugs or is_gore:
                return True
    except Exception as e:
        print(f"hata: {e}")
    return False

# --- video/gif tarama ---
async def scan_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / (fps if fps > 0 else 25)
    
    # videonun içine saklananları yakalamak için 5 farklı noktadan kare alır
    points = [0.5, duration*0.25, duration*0.5, duration*0.75, duration-0.5]
    
    for p in points:
        if p < 0: continue
        cap.set(cv2.CAP_PROP_POS_MSEC, p * 1000)
        success, frame = cap.read()
        if success:
            tmp = f"v_{p}.jpg"
            cv2.imwrite(tmp, frame)
            bad = check_content(tmp)
            os.remove(tmp)
            if bad:
                cap.release()
                return True
    cap.release()
    return False

# --- ana koruma ---
async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message
    file_id = None
    is_video = False

    # foto, stc (sticker), gif ve video - hepsini aynı sepete koyar
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
            
            # sticker dahil her şeyi aynı hassas filtreyle tarar
            forbidden = await scan_video(local_path) if is_video else check_content(local_path)
            
            if os.path.exists(local_path): os.remove(local_path)
            
            if forbidden:
                await msg.delete()
        except:
            pass

if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot_app = ApplicationBuilder().token(token).build()
    
    bot_app.add_handler(CommandHandler("start", start))
    # her türlü medyayı (photo, sticker, video, animation) dinler
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO | filters.Document.IMAGE, guard))
    
    bot_app.run_polling(drop_pending_updates=True)
