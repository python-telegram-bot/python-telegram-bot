#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from telethon.tl.types import BotInlineMessageText
import logging
from telethon.tl.types import BotInlineResult

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from get_mess import get_mes
from telegram.bot import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram.message
import telegram.chat
import datetime
# from telethon.tl.functions.messages import GetHistoryRequest

from telethon.tl.functions.channels import GetMessagesRequest

# obj=telegram.Message('@namtestgroup',from_user=None,date=datetime.datetime.date,chat=telegram.chat.Chat)
# print(obj)
obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
# get name by username id
print(obj.get_chat_member('@namtestgroup',1034090550).user.username)
# print(obj.get_chat('@namtestgroup'))
'''
sec=GetMessagesRequest('@namtestgroup',id=[42])
print('getMessageRequest -',sec)


obj1=Message('-1001192378669',from_user='hoai97nambot',date=datetime.datetime(2020,10,1),chat='namtestgroup')
print(obj1.text_html)

'''
# obj2=GetHistoryRequest('@namtestgroup', offset_id=None,offset_date=None,add_offset=None,limit=10,\
#     max_id=None, min_id=None, hash='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
# print(obj2)
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# BotInlineMessageText("hello")
a=get_mes()[-1]
st='📸 '+ a[a.find('](')+2:a.find('))')]
ad='🔥 Get more likes & comments by joining our other groups👇 \n \
❤️Happy engaging❤️ \n \
🚀Viral Network🚀'
##print(a[0])
keyboard = [[InlineKeyboardButton("✅   Rules   ✅", url='https://t.me/nam97hoai', callback_data='1'),
                 InlineKeyboardButton("📄   List    📄", url='https://t.me/hoai97nambot',callback_data='2')],

                [InlineKeyboardButton("💎   Premium User    💎", url='https://t.me/hoai97nambot', callback_data='3')]]

reply_markup = InlineKeyboardMarkup(keyboard)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    b='\n'.join(a)
    update.message.reply_text(b,disable_web_page_preview=True)
'''
def list(update, context):
    """Send a message when the command /start is issued."""
##    a=get_mes()
##    print(a)
    update.message.reply_text('a')
    '''
def help_command(update, context):
    """Send a message when the command /help is issued."""
    # update.message.reply_text('Help!'+ str(update.message.from_user.username))
    update.message.reply_text(str(update))
#
#===========================================================================================
def check_condition_messtopost(link):
    try:
        if link[:4] == 'dx30':
            auto_send_message(st)
        else:
            auto_send_message('your type is not right format')
    except(...):
        auto_send_message('your type is not right format')
#==========================================================================================
def echo(update, context):
    """Echo the user message."""
    a=update.message
    print(type(a))
    check_condition_messtopost(update.message.text)
    update.message.reply_text(update.message.text)

def auto_send_message(st):
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    
    obj.send_message('@namtestgroup',st, disable_web_page_preview=True,reply_markup=reply_markup)
def post_ad(ad):
    import time
    while True:
        obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')  
        obj.send_message('@namtestgroup',ad, disable_web_page_preview=True)
        time.sleep(5*60)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4", use_context=True)
    # obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    # st='📸 '+ a[-1]
    # obj.send_message('@innertest',st, reply_markup=reply_markup)
    for i in range(30):
        auto_send_message(st)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    


if __name__ == '__main__':
    main()
    # post_ad(ad)
