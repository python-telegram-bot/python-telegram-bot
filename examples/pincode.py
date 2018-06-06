#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example shows how to use several aspects of PTB library.

Usage:
Send /start to start interaction with bot.
Send /help to receive help message.
Send /lock XXX where XXX refers to several digits.
Send /unlock to get inline keyboard

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


HELP_MESSAGE = """
Welcome to PINCODE example.

You can use these commands:
/lock 1234 - lock the bot with the 1234 code
/unlock - unlock the bot through entering pin code on the inline keyboard
/help - show this message
"""

ENTERING = 'entering'

DIGITS = [str(i) for i in range(10)]


def locked_command(command):
    """decorator that block some commands if pin is setted"""
    def wrapper(bot, update, args, user_data):
        if 'pin' in user_data:
            update.message.reply_text('You should unlock the bot first')
        else:
            command(bot, update, args, user_data)
    return wrapper


def make_reply_message(entering_pin, extra_message=''):
    """Returns correct message that contain entered digits"""
    message = '{extra}PIN: {pin}'.format(
        extra=extra_message,
        pin=entering_pin)
    return message


def make_reply_markup():
    """Return markup with pin keyboard"""
    keyboard = [
        [InlineKeyboardButton('1', callback_data='1'),
         InlineKeyboardButton('2', callback_data='2'),
         InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'),
         InlineKeyboardButton('5', callback_data='5'),
         InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'),
         InlineKeyboardButton('8', callback_data='8'),
         InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('<', callback_data='delete'),
         InlineKeyboardButton('0', callback_data='0'),
         InlineKeyboardButton('X', callback_data='clear')],
        [InlineKeyboardButton('Enter', callback_data='enter')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def start_command(bot, update):
    """Enter point for bot. Reply some hardcoded text"""
    update.message.reply_text('You succesfully launch the PINCODE example. '
                              'Type /help for more information')


def help_command(bot, update):
    """Send additional information about bot"""
    update.message.reply_text(HELP_MESSAGE)


@locked_command
def lock_command(bot, update, args, user_data):
    """Lock the bot with provided pin code"""
    if len(args) != 1:
        update.message.reply_text(
            'You should provide some pin code to lock the bot')
    elif not args[0].isdigit():
        update.message.reply_text('Pin code can only contains digits')
    else:
        user_data['pin'] = args[0]
        update.message.reply_text('Pin code has been setted')


def unlock_command(bot, update, user_data):
    """Start unlocking the bot"""
    update.message.reply_text('Please enter the pin code')
    reply_text = make_reply_message('')
    reply_markup = make_reply_markup()
    message = update.message.reply_text(reply_text, reply_markup=reply_markup)

    # save id of message with keyboard so we can remove it in case of /cancel
    # command
    user_data['entering_message'] = message.message_id
    return ENTERING


def inline_callback(bot, update, user_data):
    """Handle buttons from pin keyboard"""
    query = update.callback_query
    choice = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    entering_pin = user_data.get('entering_pin', '')
    if choice in DIGITS:
        entering_pin += choice
        new_message = make_reply_message(entering_pin)

    elif choice == 'enter':
        # check if the entering pin is correct
        if user_data['entering_pin'] == user_data['pin']:
            bot.edit_message_text(
                'Correct!', chat_id=chat_id, message_id=message_id)
            user_data.clear()
            return ConversationHandler.END
        else:
            entering_pin = ''
            new_message = make_reply_message(
                entering_pin, extra_message='WRONG!!!\n')

    elif choice == 'delete':
        # delete last digit
        if not entering_pin:
            new_message = make_reply_message(
                entering_pin, extra_message='NO DIGIT TO DELETE\n')
        else:
            entering_pin = entering_pin[:-1]
            new_message = make_reply_message(entering_pin)

    elif choice == 'clear':
        # remove all digits
        if not entering_pin:
            new_message = make_reply_message(
                entering_pin, extra_message='NO DIGITS TO CLEAR\n')
        else:
            entering_pin = ''
            new_message = make_reply_message(entering_pin)

    user_data['entering_pin'] = entering_pin
    bot.edit_message_text(
        text=new_message, chat_id=chat_id,
        message_id=message_id, reply_markup=make_reply_markup())

    return ENTERING


def cancel_command(bot, update, user_data):
    """Handle /cancel command.

    Should clear user_data and remove inlinekeyboard"""
    keyboard_message = user_data['entering_message']
    bot.edit_message_text(
        'Haha, you gave up!', chat_id=update.message.chat_id,
        message_id=keyboard_message)
    user_data.clear()

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    # Create the EventHandler and pass it your bot's token and proxy settings.
    updater = Updater(os.environ('TOKEN'))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handler for /start command
    start_handler = CommandHandler('start', start_command)
    dp.add_handler(start_handler)

    # Add handler for /help command
    help_handler = CommandHandler('help', help_command)
    dp.add_handler(help_handler)

    # Add handler for /lock command
    lock_handler = CommandHandler(
        'lock', lock_command, pass_args=True, pass_user_data=True)
    dp.add_handler(lock_handler)

    # Add handler for unlock process
    unlock_handler = ConversationHandler(
        # Start unlocking process if /unlock command is received
        entry_points=[
            CommandHandler('unlock', unlock_command, pass_user_data=True)],

        # Handle pin keyboard buttons
        states={
            ENTERING: [
                CallbackQueryHandler(inline_callback, pass_user_data=True)]
        },

        # Cancel unlocking process if /cancel command is received
        fallbacks=[
            CommandHandler('cancel', cancel_command, pass_user_data=True)]
    )

    dp.add_handler(unlock_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
