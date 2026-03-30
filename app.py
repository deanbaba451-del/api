import os, threading, requests
from flask import Flask
from telebot import TeleBot

app = Flask(__name__)
token = "8694195722:AAH35-tlnnX2GpiHoSrYWCO7KUTe6cfGMxw"
bot = TeleBot(token)

# Sightengine API Bilgileri
API_USER = "1773861365"
API_SECRET = "8694195722:AAH35-tlnnX2GpiHoSrYWCO7KUTe6cfGMxw"

def check_ai(url):
    params = {'url': url, 'models': 'nudity-2.0,wad,drugs', 'api_user': API_USER, 'api_secret': API_SECRET}
    try:
        r = requests.get('https://api.sightengine.com/1.0/check.json', params=params).json()
        if r.get('status') == 'success':
            # Çıplaklık, Silah veya Uyuşturucu tespiti
            if r.get('nudity', {}).get('sexual_activity', 0) > 0.5 or \
               r.get('weapon', 0) > 0.5 or \
               r.get('drugs', 0) > 0.5:
                return True
    except: pass
    return False

def kill(m):
    try:
        bot.delete_message(m.chat.id, m.message_id)
        print("hasretsex")
    except: pass

@app.route('/')
def hasretsex(): return "hasretsex"

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "add me to your group")

@bot.message_handler(content_types=['new_chat_members'])
def added(m):
    if any(u.id == bot.get_me().id for u in m.new_chat_members):
        bot.send_message(m.chat.id, "i’m ready to delete inappropriate content.")

@bot.message_handler(content_types=['photo', 'video', 'sticker'])
def filter_media(m):
    if m.photo or m.video:
        fid = m.photo[-1].file_id if m.photo else m.video.file_id
        furl = f"https://api.telegram.org/file/bot{token}/{bot.get_file(fid).file_path}"
        if check_ai(furl): kill(m)
    elif m.sticker:
        bad = ["porn", "sex", "drug", "weed", "weapon", "silah", "+18"]
        if any(w in (m.sticker.set_name or "").lower() for w in bad): kill(m)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host='0.0.0.0', port=port)
