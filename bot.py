import os
import requests
import time
import threading
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo e monitor blocchi Bitcoin!")

async def showid(update, context):
    chat = update.effective_chat
    await update.message.reply_text(f"👀 Chat ID: {chat.id}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("showid", showid))

def get_bitcoin_height():
    url = "https://api.blockcypher.com/v1/btc/main"
    r = requests.get(url)
    data = r.json()
    return data.get("height")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": GROUP_ID, "text": text})

last_height = None

def watcher():
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

thread = threading.Thread(target=watcher, daemon=True)
thread.start()

app.run_polling()
