#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains an object that represents a Telegram PreparedKeyboardButton."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import (
    JSONDict,
)


class PreparedKeyboardButton(TelegramObject):
    """
    Describes a keyboard button to be used by a user of a Mini App.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    .. versionadded:: NEXT.VERSION

    Args:
        id (:obj:`int`): Unique identifier of the keyboard button.

    Attributes:
        id (:obj:`int`): Unique identifier of the keyboard button.
    """

    __slots__ = ("id",)

    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.id: int = id
        self._id_attrs = (self.id,)
        self._freeze()
