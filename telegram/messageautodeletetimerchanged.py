#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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
"""This module contains an object that represents a change in the Telegram message auto
deletion."""

from typing import Any

from telegram import TelegramObject


class MessageAutoDeleteTimerChanged(TelegramObject):
    """This object represents a service message about a change in auto-delete timer settings.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_auto_delete_time` is equal.

    .. versionadded:: 13.4

    Args:
        message_auto_delete_time (:obj:`int`): New auto-delete time for messages in the
            chat.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        message_auto_delete_time (:obj:`int`): New auto-delete time for messages in the
            chat.

    """

    def __init__(
        self,
        message_auto_delete_time: int,
        **_kwargs: Any,
    ):
        self.message_auto_delete_time = int(message_auto_delete_time)

        self._id_attrs = (self.message_auto_delete_time,)
