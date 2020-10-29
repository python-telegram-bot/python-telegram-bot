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
from get_mess import get_mes, get_mes2
from telegram.bot import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram.message
import telegram.chat
import datetime
import time

from check_follow import check_follow_yet
# from telethon.tl.functions.messages import GetHistoryRequest

from telethon.tl.functions.channels import GetMessagesRequest

# obj=telegram.Message('@namtestgroup',from_user=None,date=datetime.datetime.date,chat=telegram.chat.Chat)
# print(obj)
obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
# get name by username id

print(obj.get_chat_member('@namtestgroup',1034090550).user.username) # viettelnguyen
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
a=get_mes()
print('***************************')
container=[]
count=1
for i in range(10):
    container.append('{}. [{}]({})'.format(count,a[i][0],a[i][1]))
    count+=1

# st='📸 '+ a[a.find('](')+2:a.find('))')]
ad='🔥 Get more likes & comments by joining our other groups👇 \n \
❤️Happy engaging❤️ \n \
🚀Viral Network🚀'
##print(a[0])
keyboard = [[InlineKeyboardButton("✅   Rules   ✅", url='https://t.me/johntendo', callback_data='1'),
                 InlineKeyboardButton("📄   List    📄", url='https://t.me/hoai97nambot',callback_data='2')],

                [InlineKeyboardButton("💎   Premium User    💎", url='https://t.me/johntendo', callback_data='3')]]

reply_markup = InlineKeyboardMarkup(keyboard)

list_markup = [[InlineKeyboardButton("🚀 Dx10 Follow chain 🚀", url='https://t.me/namtestgroup')]]
reply_markup1 = InlineKeyboardMarkup(list_markup)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    # ts='@'+update.message.from_user.username
    # update.message.reply_text('Hi!')
    # obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    # obj.send_message('@hoai97nambot','container[0]',parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup1)
    m=''
    for i in container:
        m=m+ '\n'+i
    send_to_destination(update.message.from_user.id,m)
        
    # update.message.reply_text(a,disable_web_page_preview=True),
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
    update.message.reply_text(str(update.message.message_id) +'-'+ update.message.from_user.username+'-'\
        +str(update.message.from_user.id))
    time.sleep(3)
    auto_delete_message(update.message.message_id)


#===========================================================================================
def check_condition_messtopost(link):
    try:
        if link[:4] == 'dx10' or link[:4] == 'Dx10':
            pass
        else:
            auto_send_message('your type is not right format')
    except(...):
        auto_send_message('your type is not right format')
#==========================================================================================
def echo(update, context): # important info in this function
    """Echo the user message."""
    a=update.message.text
    
    if a[:4] == 'dx10' or a[:4] == 'Dx10':
        # check_condition_messtopost(update.message.text)
        if check_follow_yet(extract_usr):
            tele_usr='@'+ update.message.from_user.username
            bot_push_message(update.message.text,tele_usr)
            # update.message.reply_text(update.message.text)
            time.sleep(5)
            auto_delete_message(update.message.message_id)
    else:
        auto_delete_message(update.message.message_id)
def send_to_destination(des,mess):
    # destination='@innertest'
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    
    obj.send_message(des,mess,parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup1)

def auto_send_message(st):
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    
    obj.send_message('@namtestgroup',st,parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup)

def bot_push_message(link, user):
    #trim input link
    if link[-1] =='/':
        link=link[:-1]
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    sub_link = link[link.find('com/')+4:-1]
    me='👤 '+user+ ' ✅ '+' Dx10 [{}]({})'.format(sub_link,link[5:])
    print(me)
    obj.send_message('@namtestgroup',me, parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup)


# this scripts used for testing 👤entrepreneurs_club01 ✅

for i in range(10):
    wrap=a[i][1]
    insta_name=wrap[wrap.find('com/')+4:-2]
    me='👤 '+a[i][0]+ ' ✅ '+' Dx10 [{}]({})'.format(insta_name,a[i][1])
    print(me)
    # auto_send_message(me)
#
def auto_delete_message(mess_id):
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    try:
        obj.delete_message('@namtestgroup',mess_id)
    except:
        print('message haven\'t been deleted yet')


def post_ad(ad):
    import time
    while True:
        obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')  
        obj.send_message('@namtestgroup',ad, disable_web_page_preview=True)
        time.sleep(5*60)

def extract_usr(a):
    lit=[]
    for i in a:
        c=i[1]
        lit.append(c[c.find('com/')+4:])
    return lit
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4", use_context=True)
    # obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    # st='📸 '+ a[-1]
    # obj.send_message('@innertest',st, reply_markup=reply_markup)

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
    