#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
This is a very simple example on how one could implement a custom error handler
"""
import logging

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext

import traceback

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# this can be your own ID, or one for a developer group/channel
BOT_DEV = 208589966


def on_error(update: Update, context: CallbackContext):
    # lets log the error before we do anything else, so this appears at least in the logs
    logger.error(msg="The following error happened while handling an update",
                 exc_info=context.error)
    # now we collect chat and user data
    chat_data = str(context.chat_data)
    user_data = str(context.user_data)
    # format_tb returns the traceback in a list. We take the traceback from the error object
    tb_list = traceback.format_tb(context.error.__traceback__)
    # now we turn the list into a string
    tb = ''.join(tb_list)
    # build the message with some markdown
    message = 'Update <pre>{}</pre> caused the error <i>{}</i>. The current chat data is ' \
              '<i>{}</i>, the user data <i>{}</i>. The traceback is as follows:\n<pre>{}</pre>'
    # and send it away
    context.bot.send_message(chat_id=BOT_DEV,
                             text=message.format(update, context.error, chat_data, user_data, tb),
                             parse_mode=ParseMode.HTML)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # when an error happens, forward the error to the error handler
    dp.add_error_handler(on_error)

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
