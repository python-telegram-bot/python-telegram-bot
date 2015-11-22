#!/usr/bin/env python

"""
This Bot uses the BotEventHandler class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered.

Usage:
Basic Echobot example, repeats messages.
Type 'stop' on the command line to stop the bot.
"""

from telegram import BotEventHandler
import logging
import sys

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


# Command Handlers
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)


def error(bot, update, error):
    print('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    eh = BotEventHandler("TOKEN")

    # Get the dispatcher to register handlers
    dp = eh.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(echo)

    # on error - print error to stdout
    dp.addErrorHandler(error)

    # Start the Bot
    eh.start_polling()

    # Start CLI-Loop
    while True:
        try:
            text = raw_input()
        except NameError:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            eh.stop()
            break

if __name__ == '__main__':
    main()

