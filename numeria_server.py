import os
import json
import logging
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# ========= Config =========
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_API_URL = os.getenv("DATAMIND_API_URL", "").strip()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("numeria-bot")

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN no está configurado en las Environment Variables.")
if not DATAMIND_API_URL:
    raise RuntimeError("DATAMIND_API_URL no está configurada en las Environment Variables.")

# ========= Flask app =========
app = Flask(__name__)

# ========= Telegram app =========
telegram_app = ApplicationBuilder().token(TOKEN).build()

# ========= Handlers =========
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋 Soy NumerIA. Envíame un código (ej. 'Código 777 💫') y lo analizo con DataMind.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = (update.message.text or "").strip()
    user_name = update.effective_user.first_name or "Usuario"
    chat_id = update.effective_chat.id

    # Mensaje inmediato para UX
    try:
        await update.message.reply_text("⏳ Analizando tu mensaje con DataMind...")
    except Exception as e:
        logger.warning(f"No se pudo enviar mensaje inicial: {e}")

    # Llamada a DataMind
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {"user": user_name, "text": user_message}
            async with session.post(
                DATAMIND_API_URL,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    interpretation = data.get("interpretation", "No se obtuvo interpretación.")
                    await context.bot.send_message(chat_id=chat_id, text=f"🧠 {interpretation}")
                else:
                    body = await resp.text()
                    logger.error(f"DataMind devolvió {resp.status}: {body}")
                    await context.bot.send_message(chat_id=chat_id, text="⚠️ No pude contactar DataMind (error remoto).")
    except Exception as e:
        logger.exception("Error consultando DataMind")
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error interno: {e}")
        except Exception:
            pass

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start_cmd))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# ========= Webhook endpoints =========
@app.route("/", methods=["GET"])
def home():
    return "✅ NumerIA Bot v2 activo (Flask + Telegram + DataMind)", 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Telegram enviará POST a esta ruta (usamos el token como path secreto)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        # Procesamos el update con Application (async)
        asyncio.run(telegram_app.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.exception("Error procesando update")
        return f"ERROR: {e}", 200  # devolver 200 para que Telegram no reintente sin fin

# Helper: endpoint para registrar/actualizar el webhook con la URL actual
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    try:
        # Detecta tu URL pública actual (Render la pasa en el Host del request)
        base_url = request.host_url.rstrip("/")
        webhook_url = f"{base_url}/{TOKEN}"

        import requests as _rq
        r = _rq.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook", params={"url": webhook_url}, timeout=15)
        return jsonify({"target": webhook_url, "telegram_response": r.json()}), 200
    except Exception as e:
        logger.exception("Error seteando webhook")
        return jsonify({"error": str(e)}), 500

# ========= Main =========
if __name__ == "__main__":
    # Modo local: útil para probar sin Gunicorn
    logger.info("🚀 Servidor NumerIA Telegram arrancando en modo desarrollo")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
