#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
import json
import base64
import os
import random

# Provide some public fallbacks so it's easy for contributors to run tests on their local machine
# These bots are only able to talk in our test chats, so they are quite useless for other
# purposes than testing.
FALLBACKS = [
    {
        'token': '579694714:AAHRLL5zBVy4Blx2jRFKe1HlfnXCg08WuLY',
        'payment_provider_token': '284685063:TEST:NjQ0NjZlNzI5YjJi',
        'chat_id': '675666224',
        'super_group_id': '-1001493296829',
        'channel_id': '@pythontelegrambottests',
        'bot_name': 'PTB tests fallback 1',
        'bot_username': '@ptb_fallback_1_bot'
    }, {
        'token': '558194066:AAEEylntuKSLXj9odiv3TnX7Z5KY2J3zY3M',
        'payment_provider_token': '284685063:TEST:YjEwODQwMTFmNDcy',
        'chat_id': '675666224',
        'super_group_id': '-1001493296829',
        'channel_id': '@pythontelegrambottests',
        'bot_name': 'PTB tests fallback 2',
        'bot_username': '@ptb_fallback_2_bot'
    }
]

GITHUB_ACTION = os.getenv('GITHUB_ACTION', None)
BOTS = os.getenv('BOTS', None)
JOB_INDEX = os.getenv('JOB_INDEX', None)
if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
    BOTS = json.loads(base64.b64decode(BOTS).decode('utf-8'))
    JOB_INDEX = int(JOB_INDEX)


def get(name, fallback):
    # If we have TOKEN, PAYMENT_PROVIDER_TOKEN, CHAT_ID, SUPER_GROUP_ID,
    # CHANNEL_ID, BOT_NAME, or BOT_USERNAME in the environment, then use that
    val = os.getenv(name.upper())
    if val:
        return val

    # If we're running as a github action then fetch bots from the repo secrets
    if GITHUB_ACTION is not None and BOTS is not None and JOB_INDEX is not None:
        try:
            return BOTS[JOB_INDEX][name]
        except KeyError:
            pass

    # Otherwise go with the fallback
    return fallback


def get_bot():
    return {k: get(k, v) for k, v in random.choice(FALLBACKS).items()}
