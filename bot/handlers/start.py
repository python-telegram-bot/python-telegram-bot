from telegram import ReplyKeyboardMarkup

def start(update, context):
    keyboard = [
        ["Scrie Recenzie", "Contact"],
        ["Nota Doi"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Bun venit! Alege o opțiune din meniu:",
        reply_markup=reply_markup
    )
