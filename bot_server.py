import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token desde variable de entorno (.env en Render)
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)

# Crear la app de Telegram
telegram_app = Application.builder().token(TOKEN).build()

# --- Comandos del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ¡Hola! Soy NumerIA.\nEstoy lista para darte interpretaciones y predicciones místicas ✨."
    )

telegram_app.add_handler(CommandHandler("start", start))

# --- Rutas Flask ---
@app.route("/")
def home():
    return "NumerIA online ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    # Ejecutar proceso en el loop actual de asyncio
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(telegram_app.process_update(update))
    return "OK", 200

# --- Ejecutar Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
