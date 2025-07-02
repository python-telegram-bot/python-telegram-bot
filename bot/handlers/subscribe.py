import re
import requests
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from bot.config import EMAIL_PATTERN, WEBHOOK_URL

EMAIL = range(1)

def is_valid_email(email):
    return re.match(EMAIL_PATTERN, email)

async def abonare(update, context):
    await update.message.reply_text(
        "📩 Scrie adresa ta de email pentru a primi bonusul."
    )
    return EMAIL

async def procesare_email(update, context):
    email = update.message.text.strip()
    if not is_valid_email(email):
        await update.message.reply_text("❌ Email invalid. Încearcă din nou.")
        return EMAIL
    try:
        response = requests.post(WEBHOOK_URL, json={"email": email})
        if response.status_code == 200:
            await update.message.reply_text("✅ Email primit! Vezi inboxul.")
        else:
            await update.message.reply_text("⚠️ Eroare la trimitere.")
    except Exception:
        await update.message.reply_text("⚠️ Eroare de conexiune.")
    return ConversationHandler.END

def register_abonare_handler(app):
    abonare_handler = ConversationHandler(
        entry_points=[CommandHandler("abonare", abonare)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesare_email)]
        },
        fallbacks=[],
    )
    app.add_handler(abonare_handler)
