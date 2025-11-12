# ============================================================
#  NumerIA Bot — Conexión Telegram ↔ DataMind IA Server
#  Autor: Sergio Gastelum
#  Versión: 2.0 estable (Render compatible)
# ============================================================

import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# ------------------------------------------------------------
# 1️⃣ Cargar variables de entorno
# ------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_URL = os.getenv("DATAMIND_URL", "https://numeria-datamind.onrender.com/predict")

# ------------------------------------------------------------
# 2️⃣ Inicializar Flask y la aplicación de Telegram
# ------------------------------------------------------------
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

# ------------------------------------------------------------
# 3️⃣ Comandos del bot
# ------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔮 ¡Hola, soy *NumerIA*! ✨\n"
        "Puedo interpretar códigos, nombres o eventos con un enfoque místico y analítico.\n\n"
        "Escríbeme cualquier palabra, número o código y te daré su interpretación. 🧠",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_name = update.effective_user.first_name or "Usuario"
    await update.message.reply_text("⏳ Analizando tu mensaje...")

    try:
        response = requests.post(
            DATAMIND_URL,
            json={"user": user_name, "text": user_text},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            # Acepta tanto "interpretation" como "prediction"
            interpretation = data.get("interpretation", data.get("prediction", "No se encontró interpretación disponible."))
            await update.message.reply_text(f"🔮 *Interpretación:*\n{interpretation}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ No pude obtener respuesta de mi mente analítica (DataMind). Inténtalo de nuevo más tarde.")
    except Exception as e:
        print(f"[ERROR handle_message] {e}")
        await update.message.reply_text("🚫 Ocurrió un error al procesar tu mensaje. Inténtalo de nuevo.")

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ------------------------------------------------------------
# 4️⃣ Rutas Flask
# ------------------------------------------------------------
@app.route("/")
def home():
    return "✅ NumerIA Bot está online y escuchando."

@app.route("/webhook", methods=["POST"])
def webhook():
    """Recibe actualizaciones de Telegram y las procesa sin romper el event loop."""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)

        # Evitar 502 creando/cerrando loops en cada petición
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(telegram_app.process_update(update))
        else:
            loop.run_until_complete(telegram_app.process_update(update))

        return "OK", 200
    except Exception as e:
        print(f"[ERROR webhook] {e}")
        return "ERROR", 500

# ------------------------------------------------------------
# 5️⃣ Ejecución local / Render
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
