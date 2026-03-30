import os
import telebot
import requests
import threading
from flask import Flask

app = Flask(name)
token = "8694195722:AAGUj44Ga6rgZrl9hUiw5TUh7HDfV2j6PgE"
bot = telebot.TeleBot(token)
sightengine_user = "1773861365"
sightengine_secret = "j7Hjr6oa4CLWrPTXZfEUaujCeh4o4p6e"

settings_db = {}

def get_settings(chat_id):
    if chat_id not in settings_db:
        settings_db[chat_id] = {'nsfw': True, 'weapons': True, 'drugs': True, 'threshold': 0.60}
    return settings_db[chat_id]

def get_settings_markup(group_id):
    s = get_settings(group_id)
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton(f"nsfw: {'on' if s['nsfw'] else 'off'}", callback_data=f"tg_nsfw_{group_id}"),
        telebot.types.InlineKeyboardButton(f"weapons: {'on' if s['weapons'] else 'off'}", callback_data=f"tg_weapons_{group_id}"),
        telebot.types.InlineKeyboardButton(f"drugs: {'on' if s['drugs'] else 'off'}", callback_data=f"tg_drugs_{group_id}"),
        telebot.types.InlineKeyboardButton(f"threshold: {s['threshold']:.2f} (change)", callback_data=f"tg_thresh_{group_id}")
    )
    return markup

@app.route('/')
def index():
    return "online"

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_type = message.chat.type
    text = message.text
    if chat_type == 'private':
        if len(text.split()) > 1 and text.split()[1].startswith('set_'):
            group_id = text.split()[1].split('_')[1]
            try:
                group_id = int(group_id)
                member = bot.get_chat_member(group_id, message.from_user.id)
                if member.status in ['administrator', 'creator']:
                    s = get_settings(group_id)
                    markup = get_settings_markup(group_id)
                    bot.send_message(message.chat.id, f"settings for group {group_id}:", reply_markup=markup)
                    return
                else:
                    bot.send_message(message.chat.id, "you are not an admin of that group.")
                    return
            except Exception:
                bot.send_message(message.chat.id, "invalid group or you are not an admin.")
                return
        bot_info = bot.get_me()
        markup = telebot.types.InlineKeyboardMarkup()
        url = f"https://t.me/{bot_info.username}?startgroup=true"
        markup.add(telebot.types.InlineKeyboardButton("add me to your group", url=url))
        bot.send_message(message.chat.id, "hello. i am a moderation bot. i delete nsfw, drugs, and weapons from your groups using sightengine. add me to your group to start.", reply_markup=markup)
    else:
        bot_info = bot.get_me()
        markup = telebot.types.InlineKeyboardMarkup()
        url = f"https://t.me/{bot_info.username}?start=set_{message.chat.id}"
        markup.add(telebot.types.InlineKeyboardButton("settings", url=url))
        bot.send_message(message.chat.id, "thanks for adding me to the group. i am ready to delete inappropriate content.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tg_'))
def handle_callbacks(call):
    parts = call.data.split('_')
    action = parts[1]
    group_id = int(parts[2])
    s = get_settings(group_id)
    if action == 'nsfw':
        s['nsfw'] = not s['nsfw']
    elif action == 'weapons':
        s['weapons'] = not s['weapons']
    elif action == 'drugs':
        s['drugs'] = not s['drugs']
    elif action == 'thresh':
        s['threshold'] += 0.10
        if s['threshold'] > 0.95:
            s['threshold'] = 0.40
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_settings_markup(group_id))

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_members(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            bot_info = bot.get_me()
            markup = telebot.types.InlineKeyboardMarkup()
            url = f"https://t.me/{bot_info.username}?start=set_{message.chat.id}"
            markup.add(telebot.types.InlineKeyboardButton("settings", url=url))
            bot.send_message(message.chat.id, "thanks for adding me to the group. i am ready to delete inappropriate content.", reply_markup=markup)

@bot.message_handler(content_types=['photo', 'video', 'document', 'animation'])
def handle_media(message):
    if message.chat.type == 'private':
        return
    s = get_settings(message.chat.id)
    if not (s['nsfw'] or s['weapons'] or s['drugs']):
        return
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.animation:
        file_id = message.animation.file_id
    if not file_id:
        return
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{token}/{file_info.file_path}"
        params = {
            'models': 'nudity-2.0,weapons,recreational_drugs',
            'api_user': sightengine_user,
            'api_secret': sightengine_secret,
            'url': file_url
        }
        resp = requests.get('https://api.sightengine.com/1.0/check.json', params=params).json()
        if resp.get('status') == 'success':
            delete = False
            t = s['threshold']
            if s['nsfw'] and 'nudity' in resp:
                if resp['nudity'].get('sexual_activity', 0) >= t or resp['nudity'].get('sexual_display', 0) >= t:
                    delete = True
            if s['weapons'] and 'weapon' in resp:
                w_score = resp['weapon'].get('classes', {}).get('weapon', 0) if isinstance(resp['weapon'], dict) else resp.get('weapon', 0)
                if w_score >= t:
                    delete = True
            if s['drugs'] and 'recreational_drugs' in resp:
                d_score = resp['recreational_drugs'].get('prob', 0) if isinstance(resp['recreational_drugs'], dict) else resp.get('recreational_drugs', 0)
                if d_score >= t:
                    delete = True
            if delete:
                bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

if name == 'main':
    threading.Thread(target=bot.infinity_polling).start()
    port = 10000
    app.run(host='0.0.0.0', port=port)