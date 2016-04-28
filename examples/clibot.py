#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Example Bot to show some of the functionality of the library
# This program is dedicated to the public domain under the CC0 license.

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered, where all text inputs are
inserted into the update queue for the bot to handle.

Usage:
Repeats messages with a delay.
Reply to last chat from the command line by typing "/reply <text>"
Type 'stop' on the command line to stop the bot.
"""

from telegram.ext import Updater, StringCommandHandler, StringRegexHandler, \
    MessageHandler, CommandHandler, RegexHandler, Filters
from telegram.ext.dispatcher import run_async
from time import sleep
import logging

from future.builtins import input

# Enable Logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

# We use this var to save the last chat id, so we can reply to it
last_chat_id = 0


# Define a few (command) handler callback functions. These usually take the
# two arguments bot and update. Error handlers also receive the raised
# TelegramError object in error.
def start(bot, update):
    """ Answer in Telegram """
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    """ Answer in Telegram """
    bot.sendMessage(update.message.chat_id, text='Help!')


def any_message(bot, update):
    """ Print to console """

    # Save last chat_id to use in reply handler
    global last_chat_id
    last_chat_id = update.message.chat_id

    logger.info("New message\nFrom: %s\nchat_id: %d\nText: %s" %
                (update.message.from_user,
                 update.message.chat_id,
                 update.message.text))


@run_async
def message(bot, update):
    """
    Example for an asynchronous handler. It's not guaranteed that replies will
    be in order when using @run_async. Also, you have to include **kwargs in
    your parameter list. The kwargs contain all optional parameters that are
    """

    sleep(2)  # IO-heavy operation here
    bot.sendMessage(update.message.chat_id, text='Echo: %s' %
                                                 update.message.text)


# These handlers are for updates of type str. We use them to react to inputs
# on the command line interface
def cli_reply(bot, update, args):
    """
    For any update of type telegram.Update or str that contains a command, you
    can get the argument list by appending args to the function parameters.
    Here, we reply to the last active chat with the text after the command.
    """
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=' '.join(args))


def cli_noncommand(bot, update, update_queue):
    """
    You can also get the update queue as an argument in any handler by
    appending it to the argument list. Be careful with this though.
    Here, we put the input string back into the queue, but as a command.

    To learn more about those optional handler parameters, read the
    documentation of the Handler classes.
    """
    update_queue.put('/%s' % update)


def error(bot, update, error):
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    token = 'TOKEN'
    updater = Updater(token, workers=10)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # This is how we add handlers for Telegram messages
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    # Message handlers only receive updates that don't contain commands
    dp.add_handler(MessageHandler([Filters.text], message))
    # Regex handlers will receive all updates on which their regex matches,
    # but we have to add it in a separate group, since in one group,
    # only one handler will be executed
    dp.add_handler(RegexHandler('.*', any_message), group=1)

    # String handlers work pretty much the same. Note that we have to tell
    # the handler to pass the args or update_queue parameter
    dp.add_handler(StringCommandHandler('reply', cli_reply, pass_args=True))
    dp.add_handler(StringRegexHandler('[^/].*', cli_noncommand,
                                      pass_update_queue=True))

    # All TelegramErrors are caught for you and delivered to the error
    # handler(s). Other types of Errors are not caught.
    dp.add_error_handler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(timeout=10)

    '''
    # Alternatively, run with webhook:

    update_queue = updater.start_webhook('0.0.0.0',
                                         443,
                                         url_path=token,
                                         cert='cert.pem',
                                         key='key.key',
                                         webhook_url='https://example.com/%s'
                                             % token)

    # Or, if SSL is handled by a reverse proxy, the webhook URL is already set
    # and the reverse proxy is configured to deliver directly to port 6000:

    update_queue = updater.start_webhook('0.0.0.0', 6000)
    '''

    # Start CLI-Loop
    while True:
        text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue to be handled by our handlers
        elif len(text) > 0:
            update_queue.put(text)

if __name__ == '__main__':
    main()
