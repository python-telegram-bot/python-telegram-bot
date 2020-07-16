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
"""This module contains the classes that represent Telegram InlineQueryResult."""

from telegram import TelegramObject
from typing import Any


class InlineQueryResult(TelegramObject):
    """Baseclass for the InlineQueryResult* classes.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Attributes:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.

    Args:
        type (:obj:`str`): Type of the result.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, type: str, id: str, **kwargs: Any):
        # Required
        self.type = str(type)
        self.id = str(id)

        self._id_attrs = (self.id,)

    @property
    def _has_parse_mode(self) -> bool:
        return hasattr(self, 'parse_mode')

    @property
    def _has_input_message_content(self) -> bool:
        return hasattr(self, 'input_message_content')
