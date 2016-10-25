#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
""" This module contains helper functions """


def extract_chat_and_user(update):
    user = None
    chat = None

    if update.message:
        user = update.message.from_user
        chat = update.message.chat

    elif update.edited_message:
        user = update.edited_message.from_user
        chat = update.edited_message.chat

    elif update.inline_query:
        user = update.inline_query.from_user

    elif update.chosen_inline_result:
        user = update.chosen_inline_result.from_user

    elif update.callback_query:
        user = update.callback_query.from_user
        chat = update.callback_query.message.chat if update.callback_query.message else None

    return chat, user
