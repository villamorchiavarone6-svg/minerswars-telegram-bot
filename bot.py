import os
import time
import requests
import threading
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

API_URL = "https://api.gomining.com/api/nft-game/round/find-by-cycleId"

last_block = None

def fetch_round():
    try:
        headers = {
            "Content-Type": "application/json",
            # 👇 potresti dover mettere un header di autorizzazione se necessario
            # "Authorization": "Bearer IL_TUO_TOKEN_SE_RICHIESTO"
        }

        # se la richiesta richiede un body, aggiungi qua sotto un payload JSON
        payload = {}

        r = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        data = r.json()

        # la struttura può essere dentro "data" o simile
        # prova a esplorare se è in data["data"]["array"][0] ecc
        return data

    except Exception as e:
        print("Errore API:", e)
        return None

def watch_rounds():
    global last_block
    while True:
        result = fetch_round()
        if result:
            # Try to get round info — la struttura può variare
            # Potrebbe essere dentro data["data"]["array"][0]
            try:
                main = result.get("data", result)
                # se esiste un array round
                if "array" in main and isinstance(main["array"], list):
                    info = main["array"][0]
                else:
                    info = main

                block = info.get("blockNumber")
                active = info.get("active")

                if last_block is None:
                    last_block = block

                # block diverso o active diventato false
                if block != None and block != last_block and not active:
                    last_block = block

                    text = (
                        f"⛏️ Round trovato!\n"
                        f"📦 Block: {block}\n"
                        f"🌟 Multiplier: {info.get('multiplier')}\n"
                        f"🏆 Winner Clan: {info.get('winnerClanId')}\n"
                        f"🧑‍🏆 Winner User: {info.get('winnerUserId')}"
                    )

                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": GROUP_ID, "text": text})

            except Exception as e:
                print("Errore parsing:", e)

        time.sleep(15)  # controlla ogni 15 secondi

async def start(update, context):
    await update.message.reply_text("🤖 Bot Miner Wars attivo!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

# start watcher in new thread
thread = threading.Thread(target=watch_rounds, daemon=True)
thread.start()

app.run_polling()
