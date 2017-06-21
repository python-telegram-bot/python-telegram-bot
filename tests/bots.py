#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Provide a bot to tests"""
import os

import sys


bot_settings = {
    'APPVEYOR':
        {
            'token': '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0',
            'payment_provider_token': '284685063:TEST:ZGJlMmQxZDI3ZTc3'
        },
    'TRAVIS':
        {
            'token': '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0',
            'payment_provider_token': '284685063:TEST:ZGJlMmQxZDI3ZTc3'
        },
    'FALLBACK':
        {
            'token': '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0',
            'payment_provider_token': '284685063:TEST:ZGJlMmQxZDI3ZTc3'
        }
}


def get_bot():
    # TODO: Add version info with different bots
    # ver = sys.version_info
    # pyver = "{}{}".format(ver[0], ver[1])
    #
    bot = None
    if os.environ.get('TRAVIS', False):
        bot = bot_settings.get('TRAVIS', None)
        # TODO:
        # bot = bot_setting.get('TRAVIS'+pyver, None)
    elif os.environ.get('APPVEYOR', False):
        bot = bot_settings.get('APPVEYOR', None)
        # TODO:
        # bot = bot_setting.get('TRAVIS'+pyver, None)
    if not bot:
        bot = bot_settings['FALLBACK']

    bot.update({
        'chat_id': '12173560',
        'group_id': '-49740850',
        'channel_id': '@pythontelegrambottests'
    })
    return bot
