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
import sys

from platform import python_implementation

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
FALLBACKS = {
    'token': '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0',
    'payment_provider_token': '284685063:TEST:ZGJlMmQxZDI3ZTc3',
    'chat_id': '12173560',
    'group_id': '-49740850',
    'channel_id': '@pythontelegrambottests'
}


def get(name, fallback):
    full_name = '{0}-{1}-{2[0]}{2[1]}'.format(name, python_implementation(),
                                              sys.version_info).upper()
    # First try fullnames such as
    # TOKEN-CPYTHON-33
    # CHAT_ID-PYPY-27
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
    return {k: get(k, v) for k, v in FALLBACKS.items()}
