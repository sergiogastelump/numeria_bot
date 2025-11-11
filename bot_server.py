import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# --- Configuración básica ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)

# --- Crear loop global (persistente) ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# --- Crear aplicación Telegram sobre el loop ---
telegram_app = Application.builder().token(TOKEN).build()

# --- Comandos del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ¡Hola! Soy NumerIA. Estoy lista para darte interpretaciones y predicciones místicas.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start para comenzar o envíame un código de poder para interpretarlo 🔮")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))


# --- Página raíz ---
@app.route('/')
def index():
    return "🌐 NumerIA Bot activo y escuchando el webhook ✅", 200


# --- Webhook ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    async def process_update():
        if not telegram_app._initialized:
            await telegram_app.initialize()
        await telegram_app.process_update(update)

    # Ejecutar la tarea en el loop persistente
    loop.create_task(process_update())

    return "OK", 200


# --- Modo local ---
if __name__ == '__main__':
    print("🚀 Iniciando NumerIA Bot (modo local)...")
    app.run(host='0.0.0.0', port=10000)
