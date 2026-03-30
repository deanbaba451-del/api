import os, asyncio, requests, base64, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from flask import Flask
from threading import Thread

# --- MASTER CONFIG (GÜVENLİ ÇEKİM) ---
A = os.getenv("A") # Bot Token
B = os.getenv("B") # Github Token
C = os.getenv("C") # Render API
D = os.getenv("D") # CronJob API
E = "ethineearline" 
F = "allah-run"     
G = 6534222591     
H = {G} # Yetkili Listesi

bot = Bot(token=A)
dp = Dispatcher()
app = Flask(__name__)

@app.route('/')
def home(): return "Allah-Run Ultimate: Online"

# --- YARDIMCI FONKSİYONLAR ---
def p_t_g(f_n, c): # Github Push
    url = f"https://api.github.com/repos/{E}/{F}/contents/{f_n}"
    h = {"Authorization": f"token {B}"}
    r = requests.get(url, headers=h)
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"U: {f_n}", "content": base64.b64encode(c).decode("utf-8"), "branch": "main"}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=h).status_code in [200, 201]

def g_s_i(): # Get Render Service ID
    h = {"Authorization": f"Bearer {C}"}
    res = requests.get("https://api.render.com/v1/services", headers=h).json()
    return res[0]['service']['id'] if res else None

# --- KOMUTLAR ---
@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user.id not in H: return
    await m.answer(
        "🎭 **Allah-Run PRO Panel**\n\n"
        "✅ **Dosya At:** Github & Render anında güncellenir.\n"
        "✅ **/ls:** Repodaki dosyaları gör.\n"
        "✅ **/del [isim]:** Repodan dosya sil.\n"
        "✅ **/stop** / **/run:** Servisi durdur/başlat.\n"
        "✅ **/cj [link] [dk]:** Cron-job.org API ile ping kur.\n"
        "✅ **/logs:** Render log ekranına git."
    )

@dp.message(Command("ls"))
async def list_files(m: types.Message):
    if m.from_user.id not in H: return
    url = f"https://api.github.com/repos/{E}/{F}/contents/"
    res = requests.get(url, headers={"Authorization": f"token {B}"}).json()
    files = "\n".join([f"📄 `{f['name']}`" for f in res]) if isinstance(res, list) else "Repo boş."
    await m.answer(f"📁 **Dosyalar:**\n{files}")

@dp.message(Command("del"))
async def delete_file(m: types.Message):
    if m.from_user.id not in H: return
    try:
        fn = m.text.split()[1]
        url = f"https://api.github.com/repos/{E}/{F}/contents/{fn}"
        h = {"Authorization": f"token {B}"}
        r = requests.get(url, headers=h).json()
        if 'sha' in r:
            requests.delete(url, json={"message": f"Del: {fn}", "sha": r['sha']}, headers=h)
            await m.answer(f"🗑 `{fn}` silindi.")
    except: await m.answer("Kullanım: /del dosya.py")

@dp.message(Command("cj"))
async def setup_cron(m: types.Message):
    if m.from_user.id not in H: return
    try:
        _, link, t = m.text.split()
        api_url = "https://api.cron-job.org/jobs"
        h = {"Content-Type": "application/json", "Authorization": f"Bearer {D}"}
        data = {"job": {"title": f"AR_{F}", "url": link, "enabled": True, "schedule": {"timezone": "Europe/Istanbul", "minutes": [i for i in range(0, 60, int(t))]}}}
        if requests.put(api_url, json=data, headers=h).status_code == 200:
            await m.answer(f"✅ Cron kuruldu: {link} ({t} dk)")
    except: await m.answer("Kullanım: /cj link dk")

@dp.message(F.document)
async def handle_docs(m: types.Message):
    if m.from_user.id not in H: return
    fn = m.document.file_name
    file = await bot.get_file(m.document.file_id)
    content = await bot.download_file(file.file_path)
    msg = await m.answer(f"📤 `{fn}` yükleniyor...")
    if p_t_g(fn, content.read()):
        sid = g_s_i()
        if sid: requests.post(f"https://api.render.com/v1/services/{sid}/deploys", headers={"Authorization": f"Bearer {C}"})
        await msg.edit_text(f"✅ `{fn}` yüklendi & Deploy başladı!")
    else: await msg.edit_text("❌ Yükleme hatası!")

@dp.message(Command("stop"))
async def stop_render(m: types.Message):
    if m.from_user.id not in H: return
    sid = g_s_i()
    if requests.post(f"https://api.render.com/v1/services/{sid}/suspend", headers={"Authorization": f"Bearer {C}"}).status_code == 204:
        await m.answer("🛑 Servis durduruldu.")

@dp.message(Command("run"))
async def run_render(m: types.Message):
    if m.from_user.id not in H: return
    sid = g_s_i()
    if requests.post(f"https://api.render.com/v1/services/{sid}/resume", headers={"Authorization": f"Bearer {C}"}).status_code == 204:
        await m.answer("🚀 Servis başlatıldı.")

async def main():
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
