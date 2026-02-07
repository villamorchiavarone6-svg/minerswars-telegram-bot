import os
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo!")

app.add_handler(CommandHandler("start", start))
from telegram.ext import CommandHandler

async def showid(update, context):
    chat = update.effective_chat
    await update.message.reply_text(f"👀 Chat ID: {chat.id}")

app.add_handler(CommandHandler("showid", showid))
app.run_polling()
