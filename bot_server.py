import os
import sys
import json
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === Configuración general ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
DATAMIND_URL = os.getenv("DATAMIND_URL", "https://numeria-render-ready.onrender.com/analyze")

if not TOKEN:
    print("⚠️ ERROR: No se encontró TELEGRAM_TOKEN en las variables de entorno.")
    sys.exit(1)

app = Flask(__name__)
bot = Bot(token=TOKEN)

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
        response = req
