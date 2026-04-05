import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# flask for render keep-alive
server = Flask('')

@server.route('/')
def home():
    return "live"

def run():
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# bot setup
TOKEN = "8608358242:AAGeTBFlyRjtiQKWnaU8bCphCoQhuaPtw38"
bot = telebot.TeleBot(TOKEN)

def search_yt(query):
    opts = {'quiet': True, 'noplaylist': True, 'extract_flat': True, 'default_search': 'ytsearch5'}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
        return info['entries'] if 'entries' in info else []

@bot.message_handler(commands=['start'])
def start(message):
    text = "hello\nsend me song name or link."
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_link(message):
    download_send(message.chat.id, message.text)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    status = bot.send_message(message.chat.id, "searching...")
    results = search_yt(message.text)
    if not results:
        bot.edit_message_text("no results.", message.chat.id, status.message_id)
        return
    markup = InlineKeyboardMarkup()
    for res in results:
        title = res.get('title', 'video')[:35].lower()
        markup.add(InlineKeyboardButton(title, callback_data=f"dl_{res['id']}"))
    bot.edit_message_text("select:", message.chat.id, status.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def callback_query(call):
    url = f"https://www.youtube.com/watch?v={call.data.split('_')[1]}"
    bot.answer_callback_query(call.id, "downloading...")
    download_send(call.message.chat.id, url)

def download_send(chat_id, url):
    msg = bot.send_message(chat_id, "downloading...")
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'dl/%(title)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': True
    }
    try:
        if not os.path.exists('dl'): os.makedirs('dl')
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"
        with open(path, 'rb') as f:
            bot.send_audio(chat_id, f, title=info.get('title', 'music').lower())
        bot.delete_message(chat_id, msg.message_id)
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        bot.edit_message_text(f"error: {str(e)[:40]}", chat_id, msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
