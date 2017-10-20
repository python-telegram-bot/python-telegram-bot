#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Simple inline keyboard bot with multiple callback Query Handler.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple callbacks Query Handler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

FIRST, SECOND = range(2)

def start(bot, update):
    user = update.message.from_user
    logger.info("User %s started the conversation." % user.first_name)
    keyboard = [
        [InlineKeyboardButton(u"Next", callback_data=str(FIRST))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        u"Start handler, Press next",
        reply_markup=reply_markup
    )
    return FIRST

def first(bot, update):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton(u"Next", callback_data=str(SECOND))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"First CallbackQueryHandler, Press next"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return SECOND

def second(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Second CallbackQueryHandler"
    )
    return

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))    

def  main():
        
    # Create the Updater and pass it your bot's token. Below is an example token
    updater = Updater("476482598:AAGR26TlclQP1ZdsAbBuGy9AeCkybP8k-kA")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states FIRST and SECOND
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [CallbackQueryHandler(first)],
            SECOND: [CallbackQueryHandler(second)]
        },
        fallbacks=[CommandHandler('start', start)]
    )


    dp.add_handler(conv_handler)

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
