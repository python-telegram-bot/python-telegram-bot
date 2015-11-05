#!/usr/bin/env python

"""
This Bot uses the BotEventHandler class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Broadcaster and registered at their respective places.
Then, the bot is started and the CLI-Loop is entered, where all text inputs are
inserted into the update queue for the bot to handle.

"""

import sys
from telegram.boteventhandler import BotEventHandler
import re

global last_chat_id
last_chat_id = 0

def removeCommand(text):
    return ' '.join(text.split(' ')[1:])

""" Command Handlers """
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

def messageHandler(bot, update):
    global last_chat_id
    last_chat_id = update.message.chat_id
    bot.sendMessage(update.message.chat_id, text=update.message.text)

def errorHandler(bot, error):
    print(str(error))

def CLIReplyCommandHandler(bot, update):
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=removeCommand(update))

def unknownCLICommandHandler(bot, update):
    print("Command not found: %s" % update)

def main():
    # Create the EventHandler and pass it your bot's token
    eh = BotEventHandler("TOKEN")

    # on different commands - answer in Telegram
    eh.broadcaster.addTelegramCommandHandler("start", startCommandHandler)
    eh.broadcaster.addTelegramCommandHandler("help", helpCommandHandler)

    # on regex match - print all messages to stdout
    eh.broadcaster.addTelegramRegexHandler(re.compile('.*'), anyMessageHandler)
    
    # on CLI commands - type "/reply text" in terminal to reply to the last
    # active chat
    eh.broadcaster.addStringCommandHandler('reply', CLIReplyCommandHandler)

    # on unknown commands - answer on Telegram
    eh.broadcaster.addUnknownTelegramCommandHandler(unknownCommandHandler)

    # on unknown CLI commands - notify the user
    eh.broadcaster.addUnknownStringCommandHandler(unknownCLICommandHandler)

    # on noncommand i.e message - echo the message on Telegram
    eh.broadcaster.addTelegramMessageHandler(messageHandler)

    # on error - print error to stdout
    eh.broadcaster.addErrorHandler(errorHandler)

    # Start the Bot and store the update Queue,
    # so we can insert updates ourselves
    update_queue = eh.start()
    
    # Start CLI-Loop
    while True:
        if sys.version_info.major is 2:
            text = raw_input()
        elif sys.version_info.major is 3:
            text = input()
        
        if len(text) > 0:
            update_queue.put(text)  # Put command into queue

if __name__ == '__main__':
    main()

