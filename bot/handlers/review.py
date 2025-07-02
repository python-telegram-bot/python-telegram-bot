from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def review(update, context):
    keyboard = [
        [InlineKeyboardButton("Lasă Recenzie pe Google", url="https://g.page/r/CZW6D1JMku7KEAE/review")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Lasă o recenzie publică pentru Nota Doi aici:",
        reply_markup=reply_markup
    )
