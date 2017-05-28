#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

import logging

import telegram.ext
from telegram.ext import CommandHandler
from telegram.ext.menu import Menu, MenuHandler, Button, BackButton, ToggleButton, RadioButton

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


def submit(bot, update, menu_data):
    update.callback_query.answer()
    update.effective_message.reply_text(str(menu_data))


class MainMenu(Menu):
    def text(self, update):
        return 'Hello {}. This is the main menu!'.format(update.effective_user.first_name)

    def buttons(self):
        return [
            [Button('Test', menu=sub_menu1), Button('Test2', menu=sub_menu2)],
            [Button('Exit', callback=start)]
        ]


class SubMenu1(Menu):
    text = 'This is sub menu 1'

    def buttons(self):
        return [
            [Button('URL', url='https://google.com')],
            [Button('Recursion', menu=sub_menu1), Button('Other menu!', menu=sub_menu2)],
            [BackButton('Back')]
        ]


class SubMenu2(Menu):
    text = 'This is sub menu 2'

    buttons = [
            [
                ToggleButton('test', 'Test'),
                ToggleButton('count', states=((1, '1'), (2, '2'), (3, '3')), default=2)
            ],
            [
                RadioButton('options', 1, 'Option 1'),
                RadioButton('options', 2, 'Option 2', enabled=True),
                RadioButton('options', 3, 'Option 3')
            ],
            [
                RadioButton('custom', 1, ('[ ] Custom', '[x] Custom')),
                RadioButton('custom', 2, ('[ ] Custom 2', '[x] Custom 2'), enabled=True)
            ],
            [
                Button('Submit', submit, pass_menu_data=True),
                BackButton('Back')
            ]
        ]


main_menu = MainMenu()
sub_menu1 = SubMenu1()
sub_menu2 = SubMenu2()

dp.add_handler(MenuHandler(main_menu))
dp.add_handler(CommandHandler('menu', main_menu.start))

# Or maybe?
# dp.add_handler(MenuHandler(MainMenu, entry=CommandHandler('menu'))

dp.add_error_handler(error)

updater.start_polling()
updater.idle()
