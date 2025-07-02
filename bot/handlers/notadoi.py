from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def notadoi (update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Blog", url="https://www.notadoi.com/blog")],
        [InlineKeyboardButton("Newsletter", url="https://www.notadoi.com/newsletters/anti-scrisori-cu-intrebari-interzise-2")],
        [InlineKeyboardButton("Despre Nota Doi", url="https://www.notadoi.com/about")],
        [InlineKeyboardButton("Manifest", url="https://www.notadoi.com/manifest")],
        [InlineKeyboardButton("Cadoul Gratuit", url="https://www.notadoi.com/trilogia-codului-uman")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Alege o resursă Nota Doi:", reply_markup=reply_markup)
