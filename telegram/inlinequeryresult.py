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
InlineQueryResult"""

from telegram import TelegramObject


class InlineQueryResult(TelegramObject):
    """This object represents a Telegram InlineQueryResult.

    Attributes:
        type (str):
        id (str):

    Args:
        type (str):
        id (str): Unique identifier for this result, 1-64 Bytes

    """

    def __init__(self, type, id):
        # Required
        self.type = str(type)
        self.id = str(id)

    @staticmethod
    def de_json(data):
        return super(InlineQueryResult, InlineQueryResult).de_json(data)
