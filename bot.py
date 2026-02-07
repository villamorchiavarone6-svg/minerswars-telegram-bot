import os
import time
import requests
import threading
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))
GOMINING_JWT = os.getenv("GOMINING_JWT")

API_URL = "https://api.gomining.com/api/nft-game/round/find-by-cycleId"

last_block = None

def fetch_round():
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GOMINING_JWT}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        payload = {}

        r = requests.post(API_URL, headers=headers, json=payload, timeout=10)

        if r.status_code != 200:
            print("Errore API:", r.status_code, r.text)
            return None

        return r.json()

    except Exception as e:
        print("Errore API:", e)
        return None

def watch_rounds():
    global last_block
    while True:
        result = fetch_round()
        if result:
            try:
                main = result.get("data", result)

                if "array" in main and isinstance(main["array"], list):
                    info = main["array"][0]
                else:
                    info = main

                block = info.get("blockNumber")
                active = info.get("active")

                if last_block is None:
                    last_block = block

                if block is not None and block != last_block and not active:
                    last_block = block

                    text = (
                        f"⛏️ Round trovato!\n"
                        f"📦 Block: {block}\n"
                        f"🌟 Multiplier: {info.get('multiplier')}\n"
                        f"🏆 Winner Clan: {info.get('winnerClanId')}\n"
                        f"🧑‍🏆 Winner User: {info.get('winnerUserId')}"
                    )

                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, json={
                        "chat_id": GROUP_ID,
                        "text": text
                    })

            except Exception as e:
                print("Errore parsing:", e)

        time.sleep(15)

async def start(update, context):
    await update.message.reply_text("🤖 Bot Miner Wars attivo!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

thread = threading.Thread(target=watch_rounds, daemon=True)
thread.start()

app.run_polling()
