import os
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL")

if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada.")

app = Flask(__name__)

# Crear la app de Telegram
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Handler
async def handle_message(update, context):
    text = update.message.text
    await update.message.reply_text(f"🔮 NumerIA activo\nTu mensaje: {text}")

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/")
def home():
    return "NumerIA bot activo con PTB20 🔥", 200

if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://numeria-bot-v2.onrender.com/webhook",
        drop_pending_updates=True,
    )
