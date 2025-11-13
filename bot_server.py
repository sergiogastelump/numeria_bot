import logging
import aiohttp
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- Configuración base ---
TOKEN = "8060973627:AAFbjXs3mk624axpH4vh0kP_Cbew52YQ3zw"  # 🔐 Token del bot NumerIA
DATAMIND_API_URL = "https://numeria-datamind-eykx.onrender.com/predict"

app = Flask(__name__)

# --- Inicialización del bot de Telegram ---
telegram_app = ApplicationBuilder().token(TOKEN).build()
logging.basicConfig(level=logging.INFO)

# --- Manejador de mensajes ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat_id

    await update.message.reply_text("⏳ Analizando tu mensaje con DataMind...")

    # --- Llamada a la API DataMind ---
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"user": user_name, "text": user_message}
            async with session.post(DATAMIND_API_URL, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    respuesta = result.get("interpretation", "No se obtuvo interpretación.")
                    await context.bot.send_message(chat_id=chat_id, text=f"🧠 {respuesta}")
                else:
                    await context.bot.send_message(chat_id=chat_id, text="⚠️ Error al contactar DataMind.")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error interno: {str(e)}")

# --- Registrar el manejador ---
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook principal ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        asyncio.run(telegram_app.process_update(update))
    except Exception as e:
        print(f"❌ Error procesando update: {e}")
    return "OK", 200

# --- Página principal ---
@app.route("/", methods=["GET"])
def home():
    return "✅ Servidor NumerIA + DataMind activo y en línea", 200

# --- Ejecución en Render ---
if __name__ == "__main__":
    print("🚀 Servidor NumerIA Telegram activo y escuchando en puerto 10000")
    app.run(host="0.0.0.0", port=10000)
