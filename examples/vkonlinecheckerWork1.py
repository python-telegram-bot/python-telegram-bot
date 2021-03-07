#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import os
os.getcwd()
import sys
sys.path.append('C:\\Users\\User\\Documents\\GitHub\\python-telegram-bot\\')

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
token='8f7b3067c107b5e658eb0b9c06ac2ba6c135a97e13ceb0a8af99650870fceb5efe365f3bba70e09545c93'
checker = threading.Thread()
clients = []


queueVK = queue.Queue()
queueAvito = queue.Queue()


class Client:
    # конструктор
    def __init__(self, chatId):
        self.chatId = chatId  # устанавливаем имя
        self.vkIds = []  # устанавливаем отслеживаемые id vk
        self.avitoUsers = []  # устанавливаем отслеживаемые id avito
        self.queueVK = queue.Queue()
        self.queueAvito = queue.Queue()
        self.StatAvito = []
        self.StatVk = []

    def addVkId(self, vkId):
        self.vkIds.append(vkId)

    def addAvitoUser(self, avitoUser):
        self.avitoUsers.append(avitoUser)

    def addStatAvito(self, userUrl):
        self.StatAvito = StatAvito(userUrl)

    #def addStatVk(self, userUrl):
    #    self.StatVk = StatVk(userUrl)

class StatAvito:
    # конструктор
    def __init__(self, urlUser):
        self.urlUser = urlUser  # устанавливаем имя
        self.avitoAdsTimes = []  # список времен новых объявлений

    def addAvitoAdTimes(self, adTime):
        self.avitoAdsTimes.append(adTime)


def checkClientExist(chatId):
    for client in clients:
        if chatId == client.chatId:
            return True
    clients.append(Client(chatId))
    return False

def getClientNumber(chatId):
    for i in range(0, len(clients)):
        if chatId == clients[i].chatId:
            return i
    return None

def checkVk(url):
    f = urllib.request.urlopen(url)
    return (json.load(f))

def getHtmlAvitoUser(url):
    f = urllib.request.urlopen(url)
    mybytes = f.read()
    mystr = mybytes.decode("utf8")
    f.close()
    return mystr

def userIdCompress(userIds):
    result = ""
    for id in userIds:
        result += userIds.split('https://vk.com/')[1]
    return result

def checkOnlineVk(queueVK, update: Update):
    trackedUsers = []
    status = 0
    isCheck = 0
    while True:
        sleep(1)
        try:
            isCheck = queueVK.get(timeout=1)
            if isCheck == 0:
                break
        except queueVK.Empty:
            pass
        #https://vk.com/achtovsezaniato
        fullUrl = 'https://api.vk.com/method/users.get?user_ids=' + \
                  userIdCompress(vkIds) + \
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

def checkLastAd(queueAvito, update: Update, client: Client):
    while True:
        sleep(20)
        try:
            isCheck = queueAvito.get(timeout=1)
            if isCheck == 0:
                break
        except:
            pass
        for avitoUser in client.avitoUsers:
            html = getHtmlAvitoUser(avitoUser)
            print(1)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if (checkClientExist(update.message.chat_id)):
        update.message.reply_text('Здравствуйте, мы вас помним, список доступных команд:')
    else:
        update.message.reply_text('Добро пожаловать, это сервис по поиску и слежке, список доступных команд:')






def start_vk_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if not vkIds:
        update.message.reply_text('Воспользуйтесь командой /add_vk для добавления отслеживаемых аккаунтов')
    else:
        threading.Thread(target=checkOnlineVk, args=[queueVK, update]).start()
        queueVK.put(1)

def add_vk_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    if 'https://vk.com/' in update.message.text:
        vkIds.append(update.message.text.split(" ")[1])
        update.message.reply_text('Ссылка на юзера добавлена в список для отслеживания')

def stop_vk_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    queueVK.put(0)

def clear_vk_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    vkIds.clear()





def add_avito_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    checkClientExist(update.message.chat_id)
    clientNum = getClientNumber(update.message.chat_id)
    if 'https://www.avito.ru/user/' in update.message.text:
        clients[clientNum].addAvitoUser(update.message.text.split(" ")[1].split("&src")[0])
        update.message.reply_text('Ссылка на юзера добавлена в список для отслеживания')


def start_avito_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    clientNum = getClientNumber(update.message.chat_id)
    if not clients[clientNum].avitoUsers:
        update.message.reply_text('Воспользуйтесь командой "/add_avito *ссылка на пользователя*"  для добавления отслеживаемых аккаунтов')
    else:
        threading.Thread(target=checkLastAd, args=[clients[clientNum].queueAvito, update, clients[clientNum]]).start()
        clients[clientNum].queueAvito.put(1)



def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Пока функция не активна')

def show_command(update: Update, context: CallbackContext) -> None:
    """Echo the user message. """
    update.message.reply_text('Список отслеживаемых аккаунтов:\n')
    update.message.reply_text(vkIds)

    
def useCommands(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text('Пожалуйста, воспользуйтесь командами')


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

    dispatcher.add_handler(CommandHandler("add_avito", add_avito_command))
    dispatcher.add_handler(CommandHandler("start_avito", start_avito_command))
    #dispatcher.add_handler(CommandHandler("stop_avito", stop_avito_command))
    #dispatcher.add_handler(CommandHandler("clear_avito", clear_avito_command))

    dispatcher.add_handler(CommandHandler("start_vk", start_vk_command))
    dispatcher.add_handler(CommandHandler("add_vk", add_vk_command))
    dispatcher.add_handler(CommandHandler("stop_vk", stop_vk_command))
    dispatcher.add_handler(CommandHandler("clear_vk", clear_vk_command))

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("show", show_command))



    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, useCommands))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.

    updater.idle()



if __name__ == '__main__':
    main()
