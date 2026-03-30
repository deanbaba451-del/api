import os, threading, requests
from flask import Flask
from telebot import TeleBot, types

app = Flask(__name__)
token = "8694195722:AAH35-tlnnX2GpiHoSrYWCO7KUTe6cfGMxw"
bot = TeleBot(token)

API_USER = "1773861365"
API_SECRET = "8694195722:AAH35-tlnnX2GpiHoSrYWCO7KUTe6cfGMxw"

def check_ai(fid):
    try:
        finfo = bot.get_file(fid)
        furl = f"https://api.telegram.org/file/bot{token}/{finfo.file_path}"
        params = {'url': furl, 'models': 'nudity-2.0,wad,drugs,offensive', 'api_user': API_USER, 'api_secret': API_SECRET}
        r = requests.get('https://api.sightengine.com/1.0/check.json', params=params).json()
        if r.get('status') == 'success':
            # TOS İhlali Kontrolü (Çıplaklık, Silah, Uyuşturucu, Şiddet)
            if r.get('nudity', {}).get('sexual_activity', 0) > 0.1 or \
               r.get('weapon', 0) > 0.1 or \
               r.get('drugs', 0) > 0.1 or \
               r.get('offensive', {}).get('prob', 0) > 0.1:
                return True
    except: pass
    return False

def kill(m):
    try:
        bot.delete_message(m.chat.id, m.message_id)
        print("hasretsex")
    except: pass

@app.route('/')
def hasretsex_home(): return "hasretsex"

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup()
    # Botun kullanıcı adını otomatik alır ve gruba ekleme butonu oluşturur
    btn = types.InlineKeyboardButton("add me to your group", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
    markup.add(btn)
    bot.send_message(m.chat.id, "add me to your group", reply_markup=markup)

@bot.message_handler(content_types=['new_chat_members'])
def added(m):
    if any(u.id == bot.get_me().id for u in m.new_chat_members):
        bot.send_message(m.chat.id, "i’m ready to delete inappropriate content.")

@bot.message_handler(content_types=['photo', 'video', 'sticker'])
def filter_media(m):
    if m.photo or m.video:
        fid = m.photo[-1].file_id if m.photo else m.video.file_id
        if check_ai(fid): kill(m)
    elif m.sticker:
        bad = ["porn", "sex", "drug", "weed", "weapon", "silah", "+18"]
        txt = f"{m.sticker.set_name} {m.sticker.emoji}".lower()
        if any(w in txt for w in bad): kill(m)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: bot.infinity_polling(timeout=20, long_polling_timeout=20)).start()
    app.run(host='0.0.0.0', port=port)
