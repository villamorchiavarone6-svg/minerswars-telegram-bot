import os
import requests
import time
import threading
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

app = ApplicationBuilder().token(BOT_TOKEN).build()

# comando /start
async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo e pronto!")

app.add_handler(CommandHandler("start", start))

# (facoltativo) mostra chat id
async def showid(update, context):
    chat = update.effective_chat
    await update.message.reply_text(f"👀 Chat ID: {chat.id}")

app.add_handler(CommandHandler("showid", showid))

# --- FUNZIONI DI BLOCCO BITCOIN ---

def get_bitcoin_height():
    try:
        res = requests.get("https://api.blockcypher.com/v1/btc/main")
        return res.json().get("height")
    except:
        return None

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": GROUP_ID, "text": text})

last_height = None

def block_watcher():
    global last_height
    last_height = get_bitcoin_height()

    while True:
        try:
            current = get_bitcoin_height()
            if current and current != last_height:
                last_height = current
                send_message(f"🧱 New Bitcoin block found!\nBlock: {current}")
        except Exception as e:
            print("Error:", e)
        time.sleep(30)

# start watcher in background
thread = threading.Thread(target=block_watcher, daemon=True)
thread.start()

# start the bot
app.run_polling()
