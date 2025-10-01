import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Env var TELEGRAM_TOKEN is required")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я на PTB из репозитория 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

async def _health_tick():
    # флаг для healthcheck
    with open("/tmp/bot_healthy", "w") as f:
        f.write("ok\n")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    async def health_loop():
        while True:
            await _health_tick()
            await asyncio.sleep(10)

    async with app:
        asyncio.create_task(health_loop())
        await app.run_polling(close_loop=False)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
