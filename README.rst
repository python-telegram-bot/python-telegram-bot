from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from decouple import config

# Tokenni xavfsiz joydan o'qing
TOKEN = "7608824898:AAFYI8rNbKkHiV7yLJBb2TEGV6KptIK8BnA"

BALANCE_MESSAGE = (
    "Slayd | Презентация | Taqdimot zakaz bermoqchimisiz❓\n\n"
    "💰narxlar💰\n"
    "5 list - 10,000 so'm\n"
    "10 list - 17,000 so'm\n"
    "15 list - 25,000 so'm\n"
    "20 list - 35,000 so'm\n\n"
    "P/S: Narxlar tushirilmaydi ❌, siz to'lov qilganingizdan keyin ish boshlanadi va ishimiz 100% sifatli bo'lishiga kafolat beramiz 🤝\n\n"
    "📨 Obunchilarni bizni ish haqida fikri: @isbotm_bor\n\n"
    "\u201cAlloh albatta ustingizdan kuzatib turguvchidir\u201d (Niso surasi 1-oyat)"
)

PAYMENT_MESSAGE = (
    "✅ Buyurtma qabul qilindi!\n\n"
    "To'lov qilishingiz bilan, tayyorlanish jarayoni boshlanadi!\n\n"
    "➖ Mijozlar fikri ya'ni isbotlar: t.me/isbotm_bor\n\n"
    "➖ Click / PayMe\n\n"
    "— F.I.O: M.Tokhirha\n"
    "— Karta raqam: 9860030121000761 (Humo)\n\n"
    "❗️ To'lov qilingani haqidagi chekni yuborishni unitmang!"
)

# Start komandasi uchun tugmalar
MAIN_KEYBOARD = [
    [InlineKeyboardButton("Balance", callback_data='balance')],
    [InlineKeyboardButton("Slide qilish", callback_data='order')],
    [InlineKeyboardButton("Kanaga o'tish", url="https://t.me/Slayd_taqdimot_tayyorlash")],
    [InlineKeyboardButton("Ortga", callback_data='back')]
]

ADMIN_CONTACT_BUTTON = [
    [InlineKeyboardButton("Adminga murojaat qilish", url="https://t.me/Toxirxanov")]
]

# Komandalar va tugmalarni ishlov berish

def start(update: Update, context: CallbackContext):
    keyboard = MAIN_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Salom! Quyidagi xizmatlardan foydalanishingiz mumkin:", reply_markup=reply_markup)


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'balance':
        query.edit_message_text(BALANCE_MESSAGE, reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("To'lov qilish", callback_data='payment')]]))

    elif query.data == 'payment':
        query.edit_message_text(PAYMENT_MESSAGE, reply_markup=InlineKeyboardMarkup(ADMIN_CONTACT_BUTTON))

    elif query.data == 'order':
        query.edit_message_text("Buyurtma qabul qilish uchun admin bilan bog'laning!", reply_markup=InlineKeyboardMarkup(ADMIN_CONTACT_BUTTON))

    elif query.data == 'back':
        start(update, context)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
