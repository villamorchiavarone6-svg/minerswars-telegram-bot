import os
import time
import requests
import threading
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

# 👇 token preso da Proxyman (Authorization: Bearer XXXXX)
GOMINING_AUTH_TOKEN = os.getenv("GOMINING_AUTH_TOKEN")

API_URL = "https://api.gomining.com/api/nft-game/round/find-by-cycleId"

last_block = None


def fetch_round():
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GOMINING_AUTH_TOKEN}",
            "Accept": "application/json",
            "Origin": "https://app.gomining.com",
            "Referer": "https://app.gomining.com/",
        }

        # questo endpoint accetta body vuoto
        payload = {}

        r = requests.post(API_URL, headers=headers, json=payload, timeout=10)

        if r.status_code != 200:
            print("HTTP error:", r.status_code, r.text)
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

                if "array" in main and isinstance(main["array"], list) and len(main["array"]) > 0:
                    info = main["array"][0]
                else:
                    info = main

                block = info.get("blockNumber")
                active = info.get("active")

                if last_block is None:
                    last_block = block
                    print("Init block:", block)

                # round nuovo e concluso
                if block and block != last_block and active is False:
                    last_block = block

                    text = (
                        f"⛏️ *Nuovo round Miners Wars!*\n\n"
                        f"📦 Block: `{block}`\n"
                        f"🌟 Multiplier: {info.get('multiplier')}\n"
                        f"🏆 Winner Clan: {info.get('winnerClanId')}\n"
                        f"🧑‍🏆 Winner User: {info.get('winnerUserId')}"
                    )

                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    requests.post(
                        url,
                        json={
                            "chat_id": GROUP_ID,
                            "text": text,
                            "parse_mode": "Markdown"
                        }
                    )

            except Exception as e:
                print("Errore parsing:", e)

        time.sleep(15)


async def start(update, context):
    await update.message.reply_text("🤖 Bot Miners Wars attivo!")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

thread = threading.Thread(target=watch_rounds, daemon=True)
thread.start()

app.run_polling()
