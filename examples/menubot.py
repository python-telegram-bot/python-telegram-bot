#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Sample bot to show proof of concept menu system
# This program is dedicated to the public domain under the CC0 license.

import logging

import telegram.ext
from telegram.ext import CommandHandler
from telegram.ext.menu import MenuHandler, Button, BackButton, ToggleButton, RadioButton, \
    make_menu

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

updater = telegram.ext.Updater('225497476:AAFHMga1uS470y49vUxyutvUbpyZXxnvvnQ')
dp = updater.dispatcher


def error(bot, update, e):
    logger.warning('Update "%s" caused error "%s"' % (update, e))


def start(bot, update):
    update.effective_message.reply_text('Hello!')


def submit(bot, update, menu_data):
    update.callback_query.answer()
    update.effective_message.reply_text(str(menu_data))


main_menu = make_menu('main', lambda update: 'Hello {}. This is the main menu!'.format(
    update.effective_user.first_name), buttons=lambda update: [
    [Button('Test', menu=sub_menu1), Button('Test2', menu=sub_menu2)]
])


def sub_menu1_buttons(update):
    # NOTE: Doesn't work yet... This is because telegram doesn't send language_code for other
    # than messages. this means we are required to safe that data when we first get a message
    # and then use it afterwards. But menus don't currently pass user_data. Waiting for #1080
    lang_default = 'en_GB'
    if update and update.effective_user.language_code:
        lang_default = update.effective_user.language_code
    return [
        [Button('URL', url='https://google.com')],
        [Button('Recursion', menu=sub_menu1), Button('Other menu!', menu=sub_menu2)],
        [ToggleButton('lang', states=(('en_GB', 'English (GB)'), ('en_US', 'English (US)')),
                      default=lang_default)],
        [BackButton('Back')]
    ]


sub_menu1 = make_menu('sub_1', 'This is sub menu 1', buttons=sub_menu1_buttons)
sub_menu2 = make_menu('sub_2', 'This is sub menu 2', buttons=[
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
])

dp.add_handler(MenuHandler(main_menu))
dp.add_handler(CommandHandler('menu', main_menu.start))

# Or maybe?
# dp.add_handler(MenuHandler(MainMenu, entry=CommandHandler('menu'))

dp.add_error_handler(error)

updater.start_polling()
updater.idle()
