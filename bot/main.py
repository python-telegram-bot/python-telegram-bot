from bot.handlers.basic import register_basic_handlers
from bot.handlers.subscribe import register_abonare_handler
from bot.config import TOKEN, WEBHOOK_URL
from telegram.ext import ApplicationBuilder
import os

app = ApplicationBuilder().token(TOKEN).build()

register_basic_handlers(app)
register_abonare_handler(app)

async def run_webhook():
    print("🚀 Pornit în mod WEBHOOK")
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        url_path="/webhook",
        webhook_url=WEBHOOK_URL,
    )
    import asyncio
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_webhook())
