#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
"""This module contains an object that represents an instance of a Telegram MessageId."""
from typing import Any

from telegram._telegramobject import TelegramObject


class MessageId(TelegramObject):
    """This object represents a unique message identifier.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_id` is equal.

    Attributes:
        message_id (:obj:`int`): Unique message identifier
    """

    __slots__ = ("message_id",)

    def __init__(self, message_id: int, **_kwargs: Any):
        self.message_id = message_id

        self._id_attrs = (self.message_id,)
