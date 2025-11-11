import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Variables de entorno ===
TOKEN = os.getenv("TELEGRAM_TOKEN")

# === Inicializar Flask ===
app = Flask(__name__)

# === Configurar la app de Telegram ===
telegram_app = Application.builder().token(TOKEN).build()

# === Comando /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"[LOG] Mensaje recibido de @{update.effective_user.username}")
    await update.message.reply_text(
        "🔮 ¡Hola! Soy *NumerIA*, tu guía mística digital.\n"
        "Puedo interpretar tus códigos y vibraciones numéricas para revelar energías ocultas ✨",
        parse_mode="Markdown"
    )

# === Respuesta por defecto ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"[LOG] Mensaje: {user_text} de @{update.effective_user.username}")
    await update.message.reply_text(
        f"🌙 Has dicho: *{user_text}*\nDéjame sentir la vibración de tus palabras...",
        parse_mode="Markdown"
    )

# === Registrar handlers ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Ruta principal ===
@app.route("/")
def home():
    return "✅ NumerIA está online y lista para recibir mensajes."

# === Webhook para Telegram ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    # Crear o recuperar el loop de eventos correctamente
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_app.process_update(update))
    loop.close()

    return "OK", 200

# === Ejecutar servidor ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando NumerIA en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
