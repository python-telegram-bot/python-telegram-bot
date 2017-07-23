#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains an object that represents a Telegram KeyboardButton."""

from telegram import TelegramObject


class KeyboardButton(TelegramObject):
    """
    This object represents one button of the reply keyboard. For simple
    text buttons String can be used instead of this object to specify text
    of the button.

    Args:
        text (str):
        request_location (Optional[bool]):
        request_contact (Optional[bool]):
    """

    def __init__(self, text, request_contact=None, request_location=None, **kwargs):
        # Required
        self.text = text
        # Optionals
        self.request_contact = request_contact
        self.request_location = request_location

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return []

        keyboards = list()
        for keyboard in data:
            keyboards.append(cls.de_json(keyboard, bot))

        return keyboards
