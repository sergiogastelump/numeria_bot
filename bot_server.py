import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Variables de entorno ===
TOKEN = os.getenv("TELEGRAM_TOKEN")

# === Inicializar Flask ===
app = Flask(__name__)

# === Crear aplicación de Telegram ===
telegram_app = Application.builder().token(TOKEN).build()

# === Comando /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Mensaje recibido de @{update.effective_user.username}")
    await update.message.reply_text(
        "🔮 ¡Hola! Soy *NumerIA*, tu guía mística digital.\n"
        "Interpreto códigos, energías y vibraciones numéricas para revelar patrones ocultos ✨",
        parse_mode="Markdown"
    )

# === Respuesta a cualquier texto ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"[LOG] Mensaje: {user_text} de @{update.effective_user.username}")
    await update.message.reply_text(
        f"🌙 Has dicho: *{user_text}*\nDéjame sentir la vibración detrás de tus palabras...",
        parse_mode="Markdown"
    )

# === Registrar handlers ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Ruta base ===
@app.route("/")
def home():
    return "✅ NumerIA está online y lista para recibir mensajes."

# === Webhook de Telegram ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    # Ejecutar el procesamiento de forma asíncrona dentro del loop
    async def process():
        if not telegram_app.running:
            await telegram_app.initialize()
        await telegram_app.process_update(update)
        await telegram_app.shutdown()

    asyncio.run(process())
    return "OK", 200

# === Iniciar servidor ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
