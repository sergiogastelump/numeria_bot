import os
import sys
import json
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Configuración general ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_URL = os.getenv("DATAMIND_URL", "https://numeria-render-ready.onrender.com/analyze")

if not TOKEN:
    print("⚠️ ERROR: No se encontró TELEGRAM_TOKEN en las variables de entorno.")
    sys.exit(1)

app = Flask(__name__)

# === Inicializa la aplicación de Telegram (modo asyncio, v20+) ===
telegram_app = Application.builder().token(TOKEN).build()

# === Comandos ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ¡Hola! Soy *Numer IA Bot*, tu asistente de análisis numerológico y simbólico.\n"
        "Puedes escribirme un nombre, número o código de poder para recibir una interpretación personalizada.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Comandos disponibles:\n"
        "/start – Mensaje de bienvenida\n"
        "/help – Mostrar esta ayuda\n\n"
        "También puedes simplemente escribir un texto o número para analizarlo."
    )

async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ Por favor, envía un texto válido para analizar.")
        return

    try:
        payload = {"text": text}
        response = requests.post(DATAMIND_URL, json=payload, timeout=20)

        if response.status_code == 200:
            data = response.json()
            numerology = data.get("numerology", {})
            gematria = data.get("gematria", {})
            interp = data.get("interpretation", {}).get("summary", "Sin interpretación disponible.")

            msg = (
                f"🔢 *Análisis de:* {text}\n\n"
                f"✨ *Numerología:* {numerology.get('by_name', {}).get('name_core', 'N/A')}\n"
                f"🔠 *Gematría:* {gematria.get('gematria', 'N/A')}\n\n"
                f"🧠 *Interpretación:* {interp}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Error al procesar el análisis con el servidor DataMind.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error interno: {e}")

# === Registrar handlers ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))

# === Webhook ===
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    """Recibe las actualizaciones desde Telegram vía webhook."""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    """Página base para confirmar el estado del bot."""
    return {
        "status": "Numer IA Bot activo ✅",
        "info": "Webhook funcionando correctamente",
        "service": "bot_server"
    }, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
