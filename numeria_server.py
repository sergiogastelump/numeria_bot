import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL")

if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada.")

# Flask
app = Flask(__name__)

# Crear app de telegram (motor async)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Handler async
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"🔮 NumerIA activo\nTu mensaje: {text}")

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Inicializar PTB (una sola vez)
initialized = False

async def init_telegram():
    global initialized
    if not initialized:
        await telegram_app.initialize()
        await telegram_app.start()
        initialized = True

# Webhook endpoint (SYNC Flask → ASYNC PTB)
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    # Ejecutar proceso async dentro del loop de PTB
    loop = telegram_app.bot._async_loop

    if not loop.is_running():
        loop.run_until_complete(init_telegram())
        loop.run_until_complete(telegram_app.process_update(update))
    else:
        loop.create_task(init_telegram())
        loop.create_task(telegram_app.process_update(update))

    return "ok", 200

@app.route("/")
def home():
    return "NumerIA bot activo con PTB20 + Flask 🔥", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
