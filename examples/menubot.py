#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging

import telegram.ext
from telegram.ext import CommandHandler
from telegram.ext.menu import Menu, MenuHandler, Button, BackButton

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

updater = telegram.ext.Updater('225497476:AAGzbYE3aAYJFmOtRNqIL0qEBisdzx2xdSc')
dp = updater.dispatcher


def error(bot, update, e):
    logger.warning('Update "%s" caused error "%s"' % (update, e))


def start(bot, update):
    update.callback_query.answer()
    update.effective_message.reply_text('Hello!')


class MainMenu(Menu):
    def text(self, update):
        return 'Hello {}. This is the main menu!'.format(update.effective_user.first_name)

    def buttons(self):
        return [
            [Button('Test', menu=SubMenu1), Button('Test2', menu=SubMenu2)],
            [Button('Exit', callback=start)]
        ]


class SubMenu1(Menu):
    text = 'This is sub menu 1'

    def buttons(self):
        return [
            # [ToggleButton('Toggleable', 'on'), ToggleButton('Toggleable', 'on')],
            [Button('Recursion', menu=SubMenu1), Button('Other menu!', menu=SubMenu2)],
            [BackButton('Back')]
        ]


class SubMenu2(Menu):
    text = 'This is sub menu 2'

    buttons = [
            [Button('Start', start), Button('URL', url='https://google.com')],
            # [RadioButton('Option1', 1, group=1), RadioButton('Option2', 2, group=1)],
            [BackButton('Back')]
        ]

dp.add_handler(MenuHandler(MainMenu))
dp.add_handler(CommandHandler('menu', MainMenu.start, pass_user_data=True, pass_chat_data=True))

# Or maybe?
# dp.add_handler(MenuHandler(MainMenu, entry=CommandHandler('menu'))

dp.add_error_handler(error)

updater.start_polling()
updater.idle()
