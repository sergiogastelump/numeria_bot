# ============================================================
#  NumerIA Bot — Telegram ↔ DataMind IA
#  Versión: 3.3 Render Async Stable
#  Autor: Sergio Gastelum
# ============================================================

import os
import asyncio
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# ------------------------------------------------------------
# 1️⃣ Configuración base
# ------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_URL = os.getenv("DATAMIND_URL", "https://numeria-datamind.onrender.com/predict")

app = Flask(__name__)

# ------------------------------------------------------------
# 2️⃣ Inicializar Telegram App
# ------------------------------------------------------------
telegram_app = Application.builder().token(TOKEN).build()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(telegram_app.initialize())

print("✅ Telegram App inicializada correctamente.")

# ------------------------------------------------------------
# 3️⃣ Handlers
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
# 4️⃣ Procesamiento seguro del webhook (versión 3.3 estable)
# ------------------------------------------------------------
def process_update_async(data):
    """Procesa el update en un hilo separado sin cerrar el loop prematuramente."""
    try:
        update = Update.de_json(data, telegram_app.bot)

        async def handle():
            try:
                await telegram_app.process_update(update)
                print("✅ Update procesado correctamente.")
            except Exception as e_inner:
                print(f"[ERROR interno handle()] {e_inner}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle())
        # 🔧 No se cierra el loop manualmente para evitar RuntimeError
    except Exception as e:
        print(f"[ERROR process_update_async] {e}")

# ------------------------------------------------------------
# 5️⃣ Rutas principales Flask
# ------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "NumerIA Bot activo 🔮"}), 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook_token():
    try:
        data = request.get_json(force=True)
        print("📨 Nueva actualización (/TOKEN):", data)
        threading.Thread(target=process_update_async, args=(data,)).start()
        return "OK", 200
    except Exception as e:
        print(f"[ERROR webhook_token] {e}")
        return "ERROR", 500

# ------------------------------------------------------------
# 6️⃣ Ejecutar servidor
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA Bot en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
