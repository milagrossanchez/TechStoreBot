"""Punto de entrada: bot de Telegram para TechStore."""
import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from app.config import TELEGRAM_BOT_TOKEN
from app.services.db import init_db, guardar_mensaje, obtener_historial
from app.services.claude_client import generar_respuesta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("techstore-bot")

MENSAJE_BIENVENIDA = (
    "¡Hola! 👋 Soy el asistente virtual de *TechStore*.\n\n"
    "Te ayudo a encontrar audífonos, relojes inteligentes, cargadores y accesorios novedosos "
    "según lo que necesites. Cuéntame, ¿qué estás buscando? 🎧⌚🔌"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    guardar_mensaje(chat_id, "assistant", MENSAJE_BIENVENIDA)
    await update.message.reply_text(MENSAJE_BIENVENIDA, parse_mode="Markdown")


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    texto_usuario = update.message.text

    await update.message.chat.send_action(action="typing")

    historial = obtener_historial(chat_id)
    guardar_mensaje(chat_id, "user", texto_usuario)

    try:
        respuesta = generar_respuesta(chat_id, texto_usuario, historial)
    except Exception:
        logger.exception("Error generando respuesta del LLM")
        respuesta = "Ups, tuve un problema procesando tu mensaje. ¿Puedes intentarlo de nuevo? 🙏"

    guardar_mensaje(chat_id, "assistant", respuesta)
    respuesta_telegram = respuesta.replace("**", "*")
    try:
        await update.message.reply_text(respuesta_telegram, parse_mode="Markdown")
    except BadRequest:
        await update.message.reply_text(respuesta)


def main():
    init_db()
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    logger.info("Bot de TechStore iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()
