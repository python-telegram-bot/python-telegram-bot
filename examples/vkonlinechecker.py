#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging
import threading
import queue
import urllib.request
import json

from time import sleep

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
vkIds = []
vkStatuses = []
token='b46a44949046e5df1584001c5fe7ae4e7c2cd1047b093be5a4b9bc5e4597b2d11ff57fd2abeaad35d0b61'
checker = threading.Thread()
speed_queue = queue.Queue()

def checkVk(url):
    f = urllib.request.urlopen(url)
    return (json.load(f))

def checkOnline(speed_queue, update: Update):
    trackedUsers = []
    status = 0
    isCheck = 0
    while True:
        sleep(1)
        try:
            isCheck = speed_queue.get(timeout=1)
            if isCheck == 0:
                break
        except queue.Empty:
            pass
        #https://vk.com/achtovsezaniato
        fullUrl = 'https://api.vk.com/method/users.get?user_ids=' + \
                  vkIds[0].split('https://vk.com/')[1] + \
                  '&access_token=' +\
                  token + \
                  '&fields=online&v=5.126'
        json = checkVk(fullUrl)

        isOnline = int(json["response"][0]["online"])
        try:
            isOnlineMobile = int(json["response"][0]["online_mobile"])
        except:
            isOnlineMobile = 0
        try:
            mobileApp = int(json["response"][0]["online_app"])
        except:
            mobileApp = 0

        newStatus = isOnline
        if newStatus != status:
            status = newStatus
            if status == 1:
                if isOnlineMobile == 1:
                    update.message.reply_text("Пользователь " + vkIds[0] + " зашел в систему с телефона через приложение https://vk.com/app" + str(mobileApp))
                else:
                    update.message.reply_text(
                        "Пользователь " + vkIds[0] + " зашел в систему через компьютер")
            else:
                update.message.reply_text("Пользователь " + vkIds[0] + " вышел из системы")

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if not vkIds:
        update.message.reply_text('Добро пожаловать, можете добавить ссылку для отслеживания')
    else:
        threading.Thread(target=checkOnline, args=[speed_queue, update]).start()
        speed_queue.put(1)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Пока функция не активна')

def add_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    update.message.reply_text('Введите ссылку на юзера для его отслеживания')

def show_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    update.message.reply_text('Список отслеживаемых аккаунтов:\n')
    update.message.reply_text(vkIds)

    
def tryAddVkId(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if 'https://vk.com/' in update.message.text:
        vkIds.append(update.message.text)
        update.message.reply_text('Ссылка на юзера добавлена в список для отслеживания')

def stop_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    speed_queue.put(0)

def clear_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    vkIds.clear()

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1517729956:AAEo8WdIFETkzKx-EGCmAVh3QT1GWvzbNis", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add_command))
    dispatcher.add_handler(CommandHandler("show", show_command))
    dispatcher.add_handler(CommandHandler("stop", stop_command))
    dispatcher.add_handler(CommandHandler("clear", clear_command))



    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, tryAddVkId))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.

    updater.idle()



if __name__ == '__main__':
    main()
