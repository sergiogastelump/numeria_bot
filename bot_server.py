# bot_server.py
import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# --- Configuración ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
NUMERIA_API_URL = "https://numeria-render-ready.onrender.com/analyze"

app = Flask(__name__)
bot = Bot(token=TOKEN)


# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Bienvenido a Numer IA Tipster (webhook)*\n\n"
        "Envíame un mensaje con este formato:\n"
        "`Nombre, FechaNacimiento(YYYY-MM-DD), Código`\n\n"
        "Ejemplo:\n`Lionel Messi, 1987-06-24, MIAMI GOAL 10`",
        parse_mode="Markdown"
    )


# --- Procesamiento de mensajes ---
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) < 3:
            await update.message.reply_text("⚠️ Usa el formato correcto: Nombre, Fecha, Código")
            return

        name, birthdate, power_code = parts[0], parts[1], parts[2]
        payload = {"name": name, "birthdate": birthdate, "power_code": power_code}
        r = requests.post(NUMERIA_API_URL, json=payload, timeout=20)

        if r.status_code == 200:
            data = r.json()
            summary = data.get("interpretation", {}).get("summary", "Sin interpretación.")
            details = "\n".join(data.get("interpretation", {}).get("details", []))

            msg = (
                f"🔮 *Numer IA Tipster*\n\n"
                f"📛 *Nombre:* {name}\n"
                f"📅 *Fecha:* {birthdate}\n"
                f"💬 *Código:* {power_code}\n\n"
                f"🧠 *Resumen:* {summary}\n\n"
                f"📖 *Detalles:*\n{details}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Error al contactar Numer IA.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# --- Construcción del Application (para webhook) ---
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))


# --- Endpoint principal del webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


# --- Verificación del servidor ---
@app.route("/", methods=["GET"])
def index():
    return "Numer IA Bot online ✅", 200


# --- Iniciar Flask ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
