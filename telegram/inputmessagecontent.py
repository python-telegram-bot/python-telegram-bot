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
"""This module contains the classes that represent Telegram
InputMessageContent"""

from telegram import TelegramObject


class InputMessageContent(TelegramObject):
    """Base class for Telegram InputMessageContent Objects"""

    @staticmethod
    def de_json(data, bot):
        data = super(InputMessageContent, InputMessageContent).de_json(data, bot)

        if not data:
            return None

        try:
            from telegram import InputTextMessageContent
            return InputTextMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            from telegram import InputVenueMessageContent
            return InputVenueMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            from telegram import InputLocationMessageContent
            return InputLocationMessageContent.de_json(data, bot)
        except TypeError:
            pass

        try:
            from telegram import InputContactMessageContent
            return InputContactMessageContent.de_json(data, bot)
        except TypeError:
            pass

        return None
