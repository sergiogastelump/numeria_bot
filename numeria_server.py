import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL")

if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada en las Environment Variables.")

# Flask app
app = Flask(__name__)

# Telegram application (async)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Async handler
async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"🔮 NumerIA activo\nTu mensaje: {text}")

telegram_app.add_handler(MessageHandler(filters.TEXT, handle_message))

# Webhook route (SYNC Flask, ASYNC PTB 20)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok", 200

@app.route("/")
def index():
    return "NumerIA bot activo con PTB 20 síncrono 🔥", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
