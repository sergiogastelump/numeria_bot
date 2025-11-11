import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_URL = os.getenv("DATAMIND_URL")

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

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
            interpretation = data.get("interpretation", "No se encontró interpretación disponible.")
            await update.message.reply_text(f"🔮 *Interpretación:*\n{interpretation}", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ No pude obtener respuesta de mi mente analítica (DataMind). Inténtalo de nuevo más tarde.")
    except Exception as e:
        print(f"[ERROR] {e}")
        await update.message.reply_text("🚫 Ocurrió un error al procesar tu mensaje. Inténtalo de nuevo.")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/")
def home():
    return "✅ NumerIA Bot está online y escuchando."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    async def process():
        await telegram_app.initialize()
        await telegram_app.process_update(update)
        await telegram_app.shutdown()
    asyncio.run(process())
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
