import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Cargar variables del entorno (.env o Render)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Flask app (Render ejecuta esto con Gunicorn)
app = Flask(__name__)

# Inicializar bot (async moderno)
telegram_app = Application.builder().token(TOKEN).build()

# -------------------------------
# HANDLERS
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ¡Hola! Soy Numer IA Tipster. Envíame un código o pregunta para interpretar su energía deportiva 🔢✨")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start para comenzar o envíame un número para interpretar su significado místico en el contexto deportivo.")

# Registrar comandos
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("ayuda", ayuda))

# -------------------------------
# FLASK ROUTES
# -------------------------------
@app.route('/')
def home():
    return "✅ Numer IA Bot activo en Render", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Recibe actualizaciones desde Telegram."""
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    # Modo local (para pruebas)
    telegram_app.run_polling()
