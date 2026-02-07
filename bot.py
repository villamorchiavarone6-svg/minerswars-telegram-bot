import os
import requests
import time
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- CONFIGURAZIONE ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

# --- CREAZIONE BOT ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- HANDLER COMANDI ---

async def start(update, context):
    await update.message.reply_text("🤖 Bot attivo e pronto!")

async def showid(update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"👀 Chat ID: {chat_id}")

# Aggiungi i comandi al dispatcher
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("showid", showid))

# Opzionale: risposta a messaggi normali (solo per test)
async def on_message(update, context):
    await update.message.reply_text("👋 Ti leggo dal gruppo")

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

# --- FUNZIONE DI CONTROLLO BLOCKCHAIN ---

def get_bitcoin_height():
    """
    Legge l'altezza del blocco BTC dall'API pubblica
    """
    url = "https://api.blockcypher.com/v1/btc/main"
    r = requests.get(url)
    data = r.json()
    return data["height"]

def send_message(text):
    """
    Invia un messaggio al gruppo Telegram
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": GROUP_ID, "text": text})

# Manteniamo l'ultimo blocco noto
last_height = None

def run_block_checker():
    global last_height

    # Primo controllo iniziale
    try:
        last_height = get_bitcoin_height()
    except Exception as e:
        print("Errore iniziale API BTC:", e)

    # Ciclo infinito di controllo
    while True:
        try:
            current = get_bitcoin_height()
            if current != last_height:
                # Se c'è un nuovo blocco → inviamo notifica
                last_height = current
                send_message(f"🧱 New Bitcoin block found!\nBlock: {current}")
        except Exception as e:
            print("Errore controllo blocchi:", e)
        
        time.sleep(30)  # controlla ogni 30 secondi

# Avvia il controllo in background
import threading
block_thread = threading.Thread(target=run_block_checker, daemon=True)
block_thread.start()

# --- START BOT ---
app.run_polling()
