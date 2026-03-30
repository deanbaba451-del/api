import os
import requests
import cv2
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# --- web server ---
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
    # reply atmadan düz mesaj yazar
    await context.bot.send_message(chat_id=update.effective_chat.id, text="add me to your group")

# --- analiz motoru ---
def check_content(image_path):
    params = {
        'models': 'nudity-2.1,weapon,drugs,gore',
        'api_user': sightengine_user,
        'api_secret': sightengine_secret
    }
    try:
        with open(image_path, 'rb') as f:
            response = requests.post('https://api.sightengine.com/1.0/check.json', files={'media': f}, data=params)
        output = response.json()
        
        if output['status'] == 'success':
            # %10 ihtimal bile olsa yasaklıysa siler (çok hassas)
            nudity = any(output.get('nudity', {}).get(k, 0) > 0.1 for k in ['sexual_activity', 'sexual_display', 'erotica'])
            weapon = output.get('weapon', 0) > 0.1
            drugs = output.get('drugs', 0) > 0.1
            gore = output.get('gore', {}).get('prob', 0) > 0.1
            
            if nudity or weapon or drugs or gore:
                return True
    except Exception as e:
        print(f"hata: {e}")
    return False

# --- ana koruma ---
async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    msg = update.message
    file_id = None

    # foto, stc (sticker), gif ve video hepsini yakalar
    if msg.photo: file_id = msg.photo[-1].file_id
    elif msg.sticker: file_id = msg.sticker.file_id
    elif msg.animation or msg.video: file_id = (msg.animation or msg.video).file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith('image/'):
        file_id = msg.document.file_id

    if file_id:
        try:
            file = await context.bot.get_file(file_id)
            local_path = f"tmp_{file_id}"
            await file.download_to_drive(local_path)
            
            if check_content(local_path):
                await msg.delete() # sessizce siler
            
            if os.path.exists(local_path): os.remove(local_path)
        except:
            pass

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    bot_app = ApplicationBuilder().token(token).build()
    
    # komutlar ve filtreler
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.PHOTO | filters.Sticker | filters.ANIMATION | filters.VIDEO | filters.Document.IMAGE, guard))
    
    # eski webhook'ları temizleyip botu başlatır
    bot_app.run_polling(drop_pending_updates=True)
