import os
import requests
import time
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo e pronto!")

async def getgroupid(update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"👀 Chat ID: {chat_id}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("getgroupid", getgroupid))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

def get_bitcoin_height():
    r = requests.get("https://api.blockcypher.com/v1/btc/main")
    return r.json()["height"]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": GROUP_ID, "text": text})

last_height = None

while True:
    try:
        height = get_bitcoin_height()
        if last_height is None:
            last_height = height
        elif height > last_height:
            last_height = height
            send_message(f"🧱 New Bitcoin block found!\nBlock: {height}")
    except:
        pass
    time.sleep(30)
