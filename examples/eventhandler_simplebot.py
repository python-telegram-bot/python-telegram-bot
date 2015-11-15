#!/usr/bin/env python

"""
This Bot uses the BotEventHandler class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Broadcaster and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered.

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

    # Get the broadcaster to register handlers
    bc = eh.broadcaster

    # on different commands - answer in Telegram
    bc.addTelegramCommandHandler("start", start)
    bc.addTelegramCommandHandler("help", help)

    # on noncommand i.e message - echo the message on Telegram
    bc.addTelegramMessageHandler(echo)

    # on error - print error to stdout
    bc.addErrorHandler(error)

    # Start the Bot
    eh.start()

    # Start CLI-Loop
    while True:
        if sys.version_info.major is 2:
            text = raw_input()
        elif sys.version_info.major is 3:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            eh.stop()
            break

if __name__ == '__main__':
    main()

