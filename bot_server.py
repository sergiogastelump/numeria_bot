import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Cargar variables del entorno (.env)
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)

# Crear la aplicación de Telegram
telegram_app = Application.builder().token(TOKEN).build()

# --- COMANDOS DEL BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ¡Hola! Soy NumerIA. Estoy lista para darte interpretaciones y predicciones místicas.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start para comenzar o envíame un código de poder para interpretarlo 🔮")

# Añadir los comandos a la app
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))

# --- ENDPOINT PRINCIPAL ---
@app.route('/')
def index():
    return "NumerIA Bot está en línea ✅", 200

# --- ENDPOINT DEL WEBHOOK ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)

        # ✅ Inicializa la aplicación si no lo está
        if not telegram_app._initialized:
            await telegram_app.initialize()

        # ✅ Procesa el mensaje recibido
        await telegram_app.process_update(update)
        return "OK", 200

    except Exception as e:
        print(f"❌ Error en webhook: {e}")
        return "Error", 500


# --- MAIN LOCAL ---
if __name__ == '__main__':
    print("🚀 Iniciando NumerIA Bot en modo local...")
    app.run(host='0.0.0.0', port=10000)
