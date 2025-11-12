# ============================================================
#  NumerIA Bot — Telegram ↔ DataMind IA (Render Stable v3.0)
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
# 2️⃣ Inicializar Flask y App de Telegram
# ------------------------------------------------------------
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

# 🔧 Inicializar Telegram App al arranque
loop = asyncio.get_event_loop()
loop.run_until_complete(telegram_app.initialize())
print("✅ Telegram App inicializada correctamente.")

# ------------------------------------------------------------
# 3️⃣ Handlers principales
# ------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"📩 /start recibido de {update.effective_user.first_name}")
    await update.message.reply_text(
        "🔮 ¡Hola, soy *NumerIA*! ✨\n"
        "Puedo interpretar códigos, nombres o eventos con un enfoque místico y analítico.\n\n"
        "Escríbeme cualquier palabra, número o código y te daré su interpretación. 🧠",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_name = update.effective_user.first_name or "Usuario"
    print(f"💬 Mensaje recibido: {user_text} (de {user_name})")
    await update.message.reply_text("⏳ Analizando tu mensaje...")

    try:
        response = requests.post(
            DATAMIND_URL,
            json={"user": user_name, "text": user_text},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            interpretation = data.get("interpretation", data.get("prediction", "No se encontró interpretación."))
            await update.message.reply_text(f"🔮 *Interpretación:*\n{interpretation}", parse_mode="Markdown")
            print(f"✅ Respuesta enviada a {user_name}")
        else:
            await update.message.reply_text("⚠️ No pude obtener respuesta de DataMind.")
            print(f"⚠️ Error {response.status_code} al contactar DataMind")
    except Exception as e:
        print(f"[ERROR handle_message] {e}")
        await update.message.reply_text("🚫 Error al procesar tu mensaje.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ------------------------------------------------------------
# 4️⃣ Rutas Flask
# ------------------------------------------------------------
@app.route("/")
def home():
    return "✅ NumerIA Bot está online y escuchando."

# 🔹 Endpoint alternativo (webhook clásico)
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📨 Nueva actualización (/webhook):", data)
        update = Update.de_json(data, telegram_app.bot)

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(telegram_app.process_update(update))
        else:
            loop.run_until_complete(telegram_app.process_update(update))

        print("✅ Update procesado correctamente (/webhook).")
        return "OK", 200
    except Exception as e:
        print(f"[ERROR webhook] {e}")
        return "ERROR", 500

# 🔹 Endpoint por TOKEN (el que ahora usa Telegram)
@app.route(f"/{TOKEN}", methods=["POST"])
def token_webhook():
    try:
        data = request.get_json(force=True)
        print("📨 Nueva actualización (/TOKEN):", data)
        update = Update.de_json(data, telegram_app.bot)

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(telegram_app.process_update(update))
        else:
            loop.run_until_complete(telegram_app.process_update(update))

        print("✅ Update procesado correctamente (/TOKEN).")
        return "OK", 200
    except Exception as e:
        print(f"[ERROR token_webhook] {e}")
        return "ERROR", 500

# ------------------------------------------------------------
# 5️⃣ Ejecutar en Render
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA Bot en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
