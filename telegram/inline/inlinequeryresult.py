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
"""This module contains the classes that represent Telegram
InlineQueryResult"""

from telegram import TelegramObject


class InlineQueryResult(TelegramObject):
    """This object represents a Telegram InlineQueryResult.

    Attributes:
        type (str): Type of the result.
        id (str): Unique identifier for this result, 1-64 Bytes

    Args:
        type (str): Type of the result.
        id (str): Unique identifier for this result, 1-64 Bytes
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, type, id, **kwargs):
        # Required
        self.type = str(type)
        self.id = str(id)

        self._id_attrs = (self.id,)

    @staticmethod
    def de_json(data, bot):
        return super(InlineQueryResult, InlineQueryResult).de_json(data, bot)
