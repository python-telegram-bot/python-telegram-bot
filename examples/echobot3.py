#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import telegram
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
ECHO = range(0)

# Command handlers, usually take two params - bot and update
def start(bot, update):
    """Send a message when command /start is issued"""
    update.message.reply_text('Hello!')

def echoFunc(bot, update):
    """Echo the typed message"""
    bot.send_message(update.message.chat_id, update.message.text, reply_to_message_id=update.message.message_id)
    return ConversationHandler.END

def echo(bot, update):
    """Echo the typed message"""
    text = '/echo Bot Parrot Mode 🤖\nWhat do you want me to parrot? (Enter /cancel to end)'
    bot.send_message(update.message.chat_id, text, reply_to_message_id=update.message.message_id,
                        reply_markup=telegram.ForceReply())
    return ECHO

def cancel(bot, update):
    """Cancel the echo"""
    update.message.reply_text('🤖: Not echoing anymore!')
    return ConversationHandler.END

def error(bot, update, error):
    """Log errors caused by updates"""
    logger.warning('Update "%s" caused an error "%s"', update, error)

def main():
    """Start the bot"""
    
    # Create an event handler
    updater = Updater('TOKEN')

    # Get dispatcher to register handlers
    dp = updater.dispatcher

    # Register different commands
    dp.add_handler(CommandHandler('start', start))
    # Conversation handler to manage echo
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('echo', echo)],
        states = {
            ECHO: [MessageHandler(Filters.text, echoFunc)]
        },
        fallbacks = [CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    # Register an error logger
    dp.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__=='__main__':
    main()