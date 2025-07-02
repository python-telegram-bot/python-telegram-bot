from bot.handlers.index import index
from bot.handlers.notadoi import notadoi  # importă handlerul explicit
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
import os

# Încarcă variabilele din .env (inclusiv TOKEN-ul)
load_dotenv()
TOKEN = os.getenv("TOKEN")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Comenzi clasice (ex: /start, /notadoi)
    for k, v in index().items():
        dp.add_handler(CommandHandler(k, v))
    # Handler pentru textul exact de la buton
    dp.add_handler(MessageHandler(Filters.text("Nota Doi"), notadoi))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
