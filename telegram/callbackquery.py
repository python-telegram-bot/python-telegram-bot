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
"""This module contains a object that represents a Telegram
CallbackQuery"""

from telegram import TelegramObject, Message, User


class CallbackQuery(TelegramObject):
    """This object represents a Telegram CallbackQuery."""

    def __init__(self, id, from_user, data, **kwargs):
        # Required
        self.id = id
        self.from_user = from_user
        self.data = data
        # Optionals
        self.message = kwargs.get('message')
        self.inline_message_id = kwargs.get('inline_message_id', '')

    @staticmethod
    def de_json(data):
        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'))
        data['message'] = Message.de_json(data.get('message'))

        return CallbackQuery(**data)
