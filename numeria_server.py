import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

# Cargar variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL")

if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada en las Environment Variables.")

bot = Bot(token=TOKEN)

# Crear servidor Flask
app = Flask(__name__)

# Crear Dispatcher
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# --- Handler principal del bot ---
def handler(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text

    bot.send_message(chat_id, f"🔮 NumerIA activo\nTu mensaje: {text}")

dispatcher.add_handler(MessageHandler(Filters.text, handler))

# --- Webhook endpoint ---
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

# --- Home page ---
@app.route("/")
def index():
    return "NumerIA Bot funcionando 🔥", 200

# --- Ejecutar en Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
