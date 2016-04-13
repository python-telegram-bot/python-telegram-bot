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
InlineKeyboardButton"""

from telegram import TelegramObject


class InlineKeyboardButton(TelegramObject):
    """This object represents a Telegram InlineKeyboardButton."""

    def __init__(self,
                 text,
                 url=None,
                 callback_data=None,
                 switch_inline_query=None):
        # Required
        self.text = text

        # Optionals
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query

    @staticmethod
    def de_json(data):
        if not data:
            return None

        return InlineKeyboardButton(**data)

    @staticmethod
    def de_list(data):
        if not data:
            return []

        inline_keyboard = list()
        for inline_keyboard in data:
            inline_keyboard.append(InlineKeyboardButton.
                                   de_json(inline_keyboard))

        return inline_keyboard
