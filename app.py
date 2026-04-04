import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telegram import Bot
from telegram.error import RetryAfter

# ===== SENIN BILGILERIN =====
OWNER_ID = 6534222591
GRUP_ID = -1003664798257
API_ID = 33556742
API_HASH = '2c9797abdd74cd9522ffbb687dcd3452'

BOT_TOKENS = [
    '8379665929:AAHUik9KCJolUmyJbk-BPwIH9CxX1OUpTM8',
    '8794669149:AAGoZnHAdcLQBXVD5OJTAt1ybQi1vCZOmYg',
    '8763116353:AAEvQG3Xq0ibiplTxiy0NwiQL8s7cWUYwQM',
    '8756229068:AAHytvoIFR__2I9oOi2slZ-8bsDz8CgnR-I',
    '8771575440:AAHxNbPGSsXQscFEcuQxZvh-bNORSheHHM8'
]
# ============================

user_client = TelegramClient('user', API_ID, API_HASH)
bots = [Bot(token) for token in BOT_TOKENS]

async def get_all_members(client, chat_id):
    members = []
    offset = 0
    limit = 200
    while True:
        try:
            participants = await client(GetParticipantsRequest(
                chat_id, ChannelParticipantsSearch(''), offset, limit, hash=0
            ))
            if not participants.users:
                break
            for user in participants.users:
                members.append(user.id)
            offset += len(participants.users)
            print(f'[+] Toplanan uye: {len(members)}')
        except Exception as e:
            print(f'[-] Hata: {e}')
            break
    return members

async def ban_worker(bot, user_ids, worker_id):
    success = 0
    fail = 0
    for index, uid in enumerate(user_ids):
        try:
            await bot.ban_chat_member(GRUP_ID, uid)
            success += 1
            print(f'[BOT {worker_id}] BANLANDI: {uid} ({success}/{len(user_ids)})')
            await asyncio.sleep(0.03)
        except RetryAfter as e:
            print(f'[BOT {worker_id}] Rate limit, {e.retry_after} saniye bekleniyor')
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            fail += 1
            print(f'[BOT {worker_id}] {uid} banlanamadi: {e}')
    
    print(f'[BOT {worker_id}] Bitti: Basarili {success}, Basarisiz {fail}')

@user_client.on(events.NewMessage(pattern='\\.b', from_users=OWNER_ID))
async def start_ban(event):
    print('\n[BAŞLATILDI] Ban islemi baslatiliyor')
    
    print('[ADIM 1] Uye listesi aliniyor...')
    members = await get_all_members(user_client, event.chat_id)
    total = len(members)
    print(f'[ADIM 2] Toplam {total} uye bulundu')
    
    if total == 0:
        print('[HATA] Uye bulunamadi')
        return
    
    chunk_size = total // 5
    chunks = [members[i:i+chunk_size] for i in range(0, total, chunk_size)]
    
    print(f'[ADIM 3] 5 bot ile ban basliyor. Her bota ~{chunk_size} uye')
    
    tasks = []
    for i, bot in enumerate(bots):
        if i < len(chunks):
            tasks.append(ban_worker(bot, chunks[i], i+1))
    
    await asyncio.gather(*tasks)
    
    print(f'[TAMAM] {total} uyenin tamami banlandi')

async def main():
    await user_client.start()
    print('[HAZIR] Bot calisiyor. Gruba .b yaz')
    await user_client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())