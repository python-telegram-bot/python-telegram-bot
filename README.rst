from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Remplacez "YOUR_TOKEN" par le token d'API de votre bot
updater = Updater(token="YOUR_TOKEN", use_context=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("coucou ! Je suis votre bot conçu par DEPAYBOT99.")

def main() -> None:
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
