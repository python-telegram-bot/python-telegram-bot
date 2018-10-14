#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Provide a bot to tests"""
import os
import random
import sys

from platform import python_implementation

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
# These bots are only able to talk in our test chats, so they are quite useless for other
# purposes than testing.
FALLBACKS = [
    {
        'token': '579694714:AAHRLL5zBVy4Blx2jRFKe1HlfnXCg08WuLY',
        'payment_provider_token': '284685063:TEST:NjQ0NjZlNzI5YjJi',
        'chat_id': '675666224',
        'group_id': '-269513406',
        'channel_id': '@pythontelegrambottests'
    }, {
        'token': '558194066:AAEEylntuKSLXj9odiv3TnX7Z5KY2J3zY3M',
        'payment_provider_token': '284685063:TEST:YjEwODQwMTFmNDcy',
        'chat_id': '675666224',
        'group_id': '-269513406',
        'channel_id': '@pythontelegrambottests'
    }
]


def get(name, fallback):
    full_name = '{0}_{1}_{2[0]}{2[1]}'.format(name, python_implementation(),
                                              sys.version_info).upper()
    # First try full_names such as
    # TOKEN_CPYTHON_33
    # CHAT_ID_PYPY_27
    val = os.getenv(full_name)
    if val:
        return val
    # Then try short names
    # TOKEN
    # CHAT_ID
    val = os.getenv(name.upper())
    if val:
        return val
    # Otherwise go with the fallback
    return fallback


def get_bot():
    return {k: get(k, v) for k, v in random.choice(FALLBACKS).items()}
