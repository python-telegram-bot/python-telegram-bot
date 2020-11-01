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
import time
from check_follow import check_follow_yet, check_profile

# from telethon.tl.functions.messages import GetHistoryRequest

from telethon.tl.functions.channels import GetMessagesRequest

#obj=telegram.Message(-1001192378669,from_user=None,date=datetime.datetime.date,chat=telegram.chat.Chat)
#print(obj)
obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
# get name by username id
#print(obj.edit_message_text('@namtestgroup',1))
#print(obj.get_chat_member('@namtestgroup',1098222229).user.username) # viettelnguyen
#print(obj.get_chat_member('@namtestgroup',1098222229))

#print('.........................................................')
#auto_delete_message('1098222229') #delete warning from bot

#sec=GetMessagesRequest('@namtestgroup',id=[3,1,2])
#print('getMessageRequest -',sec)

def get_links_from_file(get_username=False):
    try:
        with open('user.txt','r') as f:
            lines=f.readlines() #include '\n' (newline)
    except:
        print('can not open links file')
    clean=[]
    for i in lines:
        if get_username == True:
            clean.append(i[i.find('com/')+4:-1])
        else:
            clean.append(i[:-1])      
    return clean


obj1=Message(1,from_user='testbot',date=datetime.datetime(2020,10,31),chat='Testbot2')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# BotInlineMessageText("hello")
def get_list():  
    a=get_links_from_file()
    container=[]
    count=1
    for i in a:
        container.append('{}. [{}]({})'.format(count,i[i.find('com/')+4:],i))
        count+=1
    return container

def get_user():
    a=get_mes()
    return a
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
    k=get_list()
    for i in k:
        m=m+ '\n'+i
    send_to_destination(update.message.from_user.id,m)
        
    # update.message.reply_text(a,disable_web_page_preview=True),

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
    aa=update.message.text
   
    if aa[:4] == 'dx10' or aa[:4] == 'Dx10':
        # check_condition_messtopost(update.message.text)
        if get_and_extract() and check_profile_link(aa):
            tele_usr='@'+ update.message.from_user.username
            bot_push_message(aa,tele_usr)
            # update.message.reply_text(update.message.text)
            time.sleep(5)
            auto_delete_message(update.message.message_id)
        else:
            update.message.reply_text('Please check following reasons: \
                ✅ No enough follow \n \
                ✅ Input link with non-exist profile \n \
                ✅ Wrong syntax',reply_markup=reply_markup1)
            auto_delete_message(update.message.message_id)
            time.sleep(5)
            auto_delete_message(update.message.message_id+1)
    elif check_profile_link(aa) and aa[:4]=='drop':
        bot_push_message(aa,'Auto Drop')   
        auto_delete_message(update.message.message_id)     
    else:
        update.message.reply_text('Wrong syntax !!!\n Please check again or read our rules',reply_markup=reply_markup1)
    
        auto_delete_message(update.message.message_id)
        time.sleep(3)
        auto_delete_message(update.message.message_id+1)
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
    sub_link = link[link.find('com/')+4:]
    me='👤 '+user+ ' ✅ '+' Dx10 [{}]({})'.format(sub_link,link[5:])
    print(me)
    obj.send_message('@namtestgroup',me, parse_mode='Markdown',disable_web_page_preview=True,reply_markup=reply_markup)


# this scripts used for testing 👤entrepreneurs_club01 ✅

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
    # get username from instagram url
    lit=[]
    for i in a:
        c=i[1]
        lit.append(c[c.find('com/')+4:])
    return lit
def get_and_extract():
    lit=get_links_from_file(get_username=True)
    r=check_follow_yet(lit)
    return r
def check_repost(usrname_in_repost_link):
    # check if a link  is able to repost
    sample = get_links_from_file(get_username=True)
    if usrname_in_repost_link in sample:
        return 0
    return 1
def check_profile_link(link):
    # check valid instagram url from user
    if link.find('https://www.instagram.com/') and check_profile(link[31:]):
        return 1
    return 0

def send_notify(content,mess_id):
    obj=Bot(token='1098222229:AAE27CLsIN1xPwoDcjrBbz-z34lualgzbB4')
    try:
        obj.send_message('@namtestgroup',content)
        time.sleep(5)
        obj.delete_message('@namtestgroup',mess_id)
    except:
        print('message haven\'t been sent/deleted yet')
        
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
