
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
Based on Echobot
This Bot uses the Updater class to handle the bot.

First, a few handler functions and class are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Conversation Echobot example, asks for words and says the whole sentence
when the users says '.'.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import Updater
import logging

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


# implement the __init__ an the __call__ method the __call__ should return whether the conversation is over.
class Echo:
    def __init__(self, chat_id, initiation_command):
        self.initiation_command = initiation_command
        self.words = []
        self.chat_id = chat_id

    def __call__(self, bot, update, *args, **kwargs):
        if update.message.text.startswith('/' + self.initiation_command):
            bot.sendMessage(self.chat_id, 'What is the first word you want me to say?')
        if update.message.text.startswith('/cancel'):
            bot.sendMessage(self.chat_id, 'The conversation is cancelled.')
            return True
        if update.message.text == '.':
            message = ''
            for word in self.words:
                message += word + ' '
            bot.sendMessage(self.chat_id, message)
            return True
        else:
            self.words.append(update.message.text)
            bot.sendMessage(self.chat_id,
                            'What is the next word you want me to say? or \'.\' for me to say all the words.')
            return False


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.addConversationHandler('start', Echo)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(echo)

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
