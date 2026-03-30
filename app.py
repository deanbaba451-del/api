import os, asyncio, requests, base64, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from flask import Flask
from threading import Thread

# --- BİLGİLERİ SİSTEMDEN ÇEK (GÜVENLİ) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
CRONJOB_API_KEY = os.getenv("CRONJOB_API_KEY")
GITHUB_USER = os.getenv("GITHUB_USER", "ethineearline") 
REPO_NAME = os.getenv("REPO_NAME", "allah-run")
OWNER_ID = int(os.getenv("OWNER_ID", "6534222591"))
AUTHORIZED_USERS = {OWNER_ID}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask(__name__)

@app.route('/')
def home(): return "Allah-Run System: Secure Mode Active"

# ... (Geri kalan tüm fonksiyonlar: push_to_github, manage_render vb. aynı kalacak) ...

async def main():
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
