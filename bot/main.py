from bot.handlers.index import index
from bot.handlers.review import review
from bot.handlers.notadoi import notadoi
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
    # Handler pentru textul de la butoane din meniu
    dp.add_handler(MessageHandler(Filters.regex(r"^Nota Doi$"), notadoi))
    dp.add_handler(MessageHandler(Filters.regex(r"^Scrie Recenzie$"), review))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
