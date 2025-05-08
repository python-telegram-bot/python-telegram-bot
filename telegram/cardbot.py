import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Your bot's token from BotFather
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

def is_valid_card(card_number):
    """Check if a card number is valid using the Luhn algorithm"""
    card_number = card_number.replace(" ", "").replace("-", "")
    if not card_number.isdigit():
        return False
    
    digits = [int(d) for d in card_number]
    checksum = 0
    
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit = digit - 9
        checksum += digit
    
    return checksum % 10 == 0

def get_card_type(card_number):
    """Identify the card type based on the card number"""
    card_number = card_number.replace(" ", "").replace("-", "")
    
    if re.match(r'^4[0-9]{12}(?:[0-9]{3})?$', card_number):
        return "Visa"
    elif re.match(r'^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$', card_number):
        return "MasterCard"
    elif re.match(r'^3[47][0-9]{13}$', card_number):
        return "American Express"
    elif re.match(r'^(6011[0-9]{12}|64[4-9][0-9]{13}|65[0-9]{14})$', card_number):
        return "Discover"
    elif re.match(r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$', card_number):
        return "Diners Club"
    elif re.match(r'^(?:2131|1800|35[0-9]{3})[0-9]{11}$', card_number):
        return "JCB"
    else:
        return "Unknown"

def start(update: Update, context: CallbackContext):
    """Send a welcome message when the command /start is issued"""
    welcome_text = """
    💳 *Payment Card Verification Bot* 💳
    
    Send me a credit card number to check:
    - If it's mathematically valid (Luhn check)
    - What card type it is (Visa, MasterCard, etc.)
    
    ⚠️ *Important*: This bot only checks format validity.
    It does NOT verify real cards or process payments.
    """
    update.message.reply_text(welcome_text, parse_mode='Markdown')

def help_command(update: Update, context: CallbackContext):
    """Send help message"""
    help_text = """
    How to use this bot:
    - Simply send a credit card number
    - The bot will tell you if it's valid
    - And identify the card type
    
    Examples of test card numbers:
    Visa: 4111 1111 1111 1111
    MasterCard: 5555 5555 5555 4444
    Amex: 3782 822463 10005
    
    ⚠️ Never share real card numbers!
    """
    update.message.reply_text(help_text)

def check_card(update: Update, context: CallbackContext):
    """Check the card number and reply with results"""
    card_number = update.message.text
    
    # Remove all non-digit characters
    cleaned_number = re.sub(r'[^0-9]', '', card_number)
    
    # Check if the message looks like a card number
    if len(cleaned_number) < 13 or len(cleaned_number) > 19 or not cleaned_number.isdigit():
        update.message.reply_text("❌ That doesn't look like a valid card number format.")
        return
    
    if is_valid_card(card_number):
        card_type = get_card_type(card_number)
        reply = f"✅ Valid {card_type} card number\n\n"
        reply += "This is a *mathematically valid* card number format.\n\n"
        reply += "⚠️ Remember: This doesn't mean the card is active or has funds."
        update.message.reply_text(reply, parse_mode='Markdown')
    else:
        update.message.reply_text("❌ Invalid card number\n\nThis number doesn't pass the Luhn check.")

def main():
    """Start the bot"""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Message handler for card numbers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, check_card))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
