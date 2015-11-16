#!/usr/bin/env python

"""
This Bot uses the BotEventHandler class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Broadcaster and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered, where all text inputs are
inserted into the update queue for the bot to handle.

Usage:
Basic Echobot example, repeats messages. Reply to last chat from the command
line by typing "/reply <text>"
Type 'stop' on the command line to stop the bot.
"""

import sys
from telegram import BotEventHandler
from telegram.broadcaster import run_async
from time import sleep
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

last_chat_id = 0


def removeCommand(text):
    return ' '.join(text.split(' ')[1:])


# Command Handlers
def startCommandHandler(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def helpCommandHandler(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def anyMessageHandler(bot, update):
    print("chat_id: %d\nFrom: %s\nText: %s" %
          (update.message.chat_id, str(update.message.from_user),
           update.message.text))


def unknownCommandHandler(bot, update):
    bot.sendMessage(update.message.chat_id, text='Command not recognized!')


@run_async
def messageHandler(bot, update):
    """
    Example for an asynchronous handler. It's not guaranteed that replies will
    be in order when using @run_async.
    """
    
    # Save last chat_id to use in reply handler
    global last_chat_id
    last_chat_id = update.message.chat_id
    
    sleep(2)  # IO-heavy operation here
    bot.sendMessage(update.message.chat_id, text=update.message.text)


def errorHandler(bot, update, error):
    print('Update %s caused error %s' % (update, error))


def CLIReplyCommandHandler(bot, update):
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=removeCommand(update))


def anyCLIHandler(bot, update, update_queue):
    """
    You can get the update queue as an argument in any handler just by adding
    it to the argument list. Be careful with this though.
    """
    update_queue.put('/%s' % update)


def unknownCLICommandHandler(bot, update):
    print("Command not found: %s" % update)


def main():
    # Create the EventHandler and pass it your bot's token.
    eh = BotEventHandler("TOKEN", workers=2)

    # Get the broadcaster to register handlers
    bc = eh.broadcaster

    # on different commands - answer in Telegram
    bc.addTelegramCommandHandler("start", startCommandHandler)
    bc.addTelegramCommandHandler("help", helpCommandHandler)

    # on regex match - print all messages to stdout
    bc.addTelegramRegexHandler('.*', anyMessageHandler)
    
    # on CLI commands - type "/reply text" in terminal to reply to the last
    # active chat
    bc.addStringCommandHandler('reply', CLIReplyCommandHandler)

    # on unknown commands - answer on Telegram
    bc.addUnknownTelegramCommandHandler(unknownCommandHandler)

    # on unknown CLI commands - notify the user
    bc.addUnknownStringCommandHandler(unknownCLICommandHandler)

    # on any CLI message that is not a command - resend it as a command
    bc.addStringRegexHandler('[^/].*', anyCLIHandler)

    # on noncommand i.e message - echo the message on Telegram
    bc.addTelegramMessageHandler(messageHandler)

    # on error - print error to stdout
    bc.addErrorHandler(errorHandler)

    # Start the Bot and store the update Queue,
    # so we can insert updates ourselves
    update_queue = eh.start_polling(poll_interval=0.1, timeout=20)
    '''
    # Alternatively, run with webhook:
    update_queue = eh.start_webhook('example.com', 443, 'cert.pem', 'key.key',
                                    listen='0.0.0.0')
    '''
    
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

        # else, put the text into the update queue
        elif len(text) > 0:
            update_queue.put(text)  # Put command into queue

if __name__ == '__main__':
    main()

