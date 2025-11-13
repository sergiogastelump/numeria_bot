import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL")

if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada en las Environment Variables.")

# Flask app
app = Flask(__name__)

# Crear app de telegram
telegram_app = Application.builder().token(TOKEN).build()

# Inicializar el event loop global
loop = asyncio.get_event_loop()

# Inicializar la app de telegram UNA SOLA VEZ
async def init_telegram():
    await telegram_app.initialize()
    await telegram_app.start()
    print("Telegram app inicializada correctamente.")

loop.run_until_complete(init_telegram())

# Handler
async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f"🔮 NumerIA activo\nTu mensaje: {text}")

telegram_app.add_handler(
    telegram_app.message_handler(filters=None)(handle_message)
)

# Webhook endpoint síncrono
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    loop.create_task(telegram_app.process_update(update))
    return "ok", 200

@app.route("/")
def index():
    return "NumerIA bot activo con webhook PTB20 🔥", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
