import random
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Render Uyku Engelleyici
app = Flask('')
@app.route('/')
def home(): return "Sistem Aktif!"
def run(): 
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run); t.daemon = True; t.start()

# Küfür Listesi
KUDURTMALAR = [
    "kes sesini ucube orospu", "yazma lan bi daha ananı siktirtme", "senin o tipini sikeyim kaşar", 
    "amına koduğumun evladı seni", "boş yapma siktir git çöplüğüne", "kudur köpek gibi orospu çocuğu",
    "senin ananı avradını sikeyim", "beş para etmez sürtük piç", "kes lan amcık ağızlı", 
    "yedi sülaleni sikeyim senin", "senin varlığını sikeyim ucube", "ananın amına beton dökeyim",
    "fahişe ruhlu ezik", "seni sike sike öldürürüm yazma", "beyni sökülmüş fahişe", "it soyu seni", 
    "suratına tükürsem şükredersin", "rezil rüsva fahişe", "senin o ses tellerini sikeyim", "kokuşmuş amlı",
    "sidikli kaşar", "seni doğuran ebeyi sikeyim", "ucube dölü", "hayatın yalan senin ezik fahişe", 
    "soyun sopun kurusun", "senin o süzme beynini sikeyim", "lağım faresi suratlı", "ucube kılıklı orospu", 
    "ebenin amına kadar yolun var", "kudur lan it", "seni kim siklesin amcık", "it gibi havlama", 
    "ananı pazarda satayım", "senin o olmayan onurunu sikeyim", "beş kuruşluk fahişe", "yüzsüz köpek", 
    "ibretlik ucube", "senin genetiğini sikeyim", "evrimini sikeyim senin", "seni sokağa salan aileyi sikeyim", 
    "kanını sikeyim", "senin o boktan hayatını sikeyim", "kudurmaktan geber", "senin mezarını sikeyim", 
    "ölünü dirini sikeyim", "seni bu dünyaya getirenin amına koyayım", "rezil rüsva", "senin o sülaleni sikeyim", 
    "sus lan am biti", "foseptik çukuru ağızlı", "gavat dölü", "senin o tipine sokayım", "sesini kes ucube karı", 
    "beyni sulanmış fahişe", "senin o boktan fikirlerini sikeyim", "eziklik abidesi", "senin o sürtük ruhunu sikeyim", 
    "lağım çukuru", "senin o kokuşmuş bedenini sikeyim", "ölünü sikeyim", "seni sokağa atan piç", 
    "senin o karakterini sikeyim", "seni bu hayata bağlayan damarı sikeyim", "kudur pislik", "ananın amına kantar girsin", 
    "seni sike sike kudurtabilirim", "ağla lan sürtük", "senin o sızlayan amını sikeyim", "beyinsiz fahişe", 
    "senin o ucube varlığını sikeyim", "rezilliğin tek adresi", "senin o sülaleni sikeyim", "yazma lan it", 
    "senin o sesini sikeyim", "kudur fahişe", "senin o olmayan beynini sikeyim", "ucube ruhlu", 
    "seni kim doğurduysa onun amına koyayım", "pislik torbası", "senin o suratını sikeyim", "ezik orospu", 
    "kudur köpek", "senin o genlerini sikeyim", "it soyu", "senin o geçmişini sikeyim", "geleceğini sikeyim", 
    "seni sike sike öldürürüm", "fahişe dölü", "seni o ucube ananı sikeyim", "yazma lan fahişe", 
    "senin o kokuşmuş ruhunu sikeyim", "rezil rüsva", "senin o sülaleni tek tek sikeyim", "ananın amına uçak motoru sokayım",
    "senin o ucube varlığın dünyaya hakaret", "ebeni süzgeçten geçireyim", "seni doğuran spermi sikeyim",
    "lağım faresi suratlı ezik", "senin o onursuz hayatını sikeyim", "beş para etmez ruhunu sikeyim",
    "ölün bile bu dünyayı kirletir", "ananın amına kantar takayım", "senin o ucube ananı sikeyim",
    "sidikli orospu", "senin o genetik atık suratını sikeyim", "hayatın boyunca bir piçten öteye geçemeyeceksin",
    "seni bu hayata bağlayan her şeyi sikeyim", "ölünü dirini her gün bir tur sikeyim", "ucube kılıklı fahişe",
    "seni o kokuşmuş bedenini akbabalara siktireyim", "foseptik ağızlı kaşar", "seni kimse siktir etmiyor mu lan",
    "senin o olmayan haysiyetini sikeyim", "kuduz köpek gibi havlama", "ezikliğin kitabını yazmışsın ucube",
    "senin o leş kokan ağzını sikeyim", "suratına tükürsem rahmet sanarsın", "ananı pazarda meze yapayım",
    "senin o boktan fikirlerini beyninle beraber sikeyim", "rezilliğin vücut bulmuş halisin", "sus lan am biti",
    "senin o geçmişindeki her saniyeyi sikeyim", "geleceğine tüküreyim soyu bozuk", "senin o süzme beynini sikeyim",
    "fahişeliğin kitabını yazmışsın", "beyni sökülmüş sürtük", "senin o tipini sikeyim aynaya bakma",
    "kudurmaktan geber ucube", "ananın amına beton döküp fabrika kurayım", "senin o sülaleni üst üste koyup sikeyim",
    "it gibi havlama sesini kes", "seni sike sike kudurtabilirim yazma", "fahişe dölü ucube",
    "senin o kokuşmuş sülaleni sikeyim", "eziklik abidesi kaşar", "senin o ucube ruhunu sikeyim",
    "beyni sulanmış fahişe dölü", "senin o karakterini sikeyim", "yedi sülaleni sikeyim senin",
    "ananın amına uçak girsin", "seni sokağa salan aileyi sikeyim", "kanını sikeyim senin",
    "senin o boktan hayatını sikeyim", "mezarına sıçayım senin", "seni kim doğurduysa onun amına koyayım"
]

targets = set()
sleep_time = 0.1  # Varsayılan hız

async def basla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        targets.add(user_id)
        await update.message.reply_to_message.reply_text(random.choice(KUDURTMALAR))

async def dur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        if user_id in targets:
            targets.remove(user_id)

async def sleep_ayar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sleep_time
    try:
        yeni_sure = float(context.args[0])
        sleep_time = yeni_sure
        await update.message.reply_text(f"yeni hız: {sleep_time} saniye")
    except (IndexError, ValueError):
        await update.message.reply_text("hız belirt: .sleep 0.5")

async def kudur_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id in targets:
        await asyncio.sleep(sleep_time)  # Belirlenen süre kadar bekler
        try:
            await update.message.reply_text(random.choice(KUDURTMALAR))
        except:
            pass

def main():
    token = "8578504590:AAFyelzmt2UroqECRHHmD9mXrtzg_g90M6c"
    keep_alive()
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("basla", basla))
    application.add_handler(CommandHandler("dur", dur))
    application.add_handler(CommandHandler("sleep", sleep_ayar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kudur_handler))

    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
