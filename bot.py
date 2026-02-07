import os
import requests
import time
import threading
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# /start
async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo!")

# /showid → SERVE SOLO PER PRENDERE IL CHAT ID
async def showid(update, context):
    chat = update.effective_chat
    await update.message.reply_text(f"👀 Chat ID: {chat.id}")

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("showid", showid))

app.run_polling()
