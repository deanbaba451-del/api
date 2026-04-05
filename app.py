import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

server = Flask('')
@server.route('/')
def home(): return "live"

def run(): server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = "8608358242:AAGeTBFlyRjtiQKWnaU8bCphCoQhuaPtw38"
bot = telebot.TeleBot(TOKEN)
promo = "done. /start for new\ncheck out: t.me/sizleriseviyombot"

def search_yt(query):
    opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True, 'default_search': 'ytsearch5'}
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            return info['entries'] if 'entries' in info else []
        except: return []

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "hello\nsend me song name for mp3 or link for video/photo.")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_link(message):
    download_media(message.chat.id, message.text, is_mp3=False)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_message(message.chat.id, "processing...")
    results = search_yt(message.text)
    if not results:
        bot.send_message(message.chat.id, "no results.")
        return
    markup = InlineKeyboardMarkup()
    for res in results:
        title = res.get('title', 'video')[:35].lower()
        markup.add(InlineKeyboardButton(title, callback_data=f"dl_{res['id']}"))
    bot.send_message(message.chat.id, "select for mp3:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_query(call):
    url = f"https://www.youtube.com/watch?v={call.data.split('_')[1]}"
    bot.answer_callback_query(call.id, "processing...")
    download_media(call.message.chat.id, url, is_mp3=True)

def download_media(chat_id, url, is_mp3):
    bot.send_message(chat_id, "processing...")
    if not os.path.exists('dl'): os.makedirs('dl')
    
    opts = {
        'format': 'bestaudio/best' if is_mp3 else 'best',
        'outtmpl': 'dl/%(title)s.%(ext)s',
        'quiet': True
    }
    if is_mp3:
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_mp3: filename = filename.rsplit('.', 1)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if is_mp3:
                bot.send_audio(chat_id, f, title=info.get('title', 'music').lower())
            else:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    bot.send_photo(chat_id, f)
                else:
                    bot.send_video(chat_id, f)
        
        bot.send_message(chat_id, promo.lower())
        # dosyayı sunucudan temizliyoruz (yük olmasın diye) ama chat mesajları duruyor.
        if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, f"error: {str(e)[:40]}")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
