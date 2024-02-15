#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains the ChatBoostAdded object."""
from typing import Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class ChatBoostAdded(TelegramObject):
    """
    This object represents a service message about a user boosting a chat.

    Objects of this class are comparable in terms of equality.
    Two objects of this class are considered equal, if their
    :attr:`boost_count` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        boost_count (:obj:`int`): Number of boosts added by the user.

    Attributes:
        boost_count (:obj:`int`): Number of boosts added by the user.

    """

    __slots__ = ("boost_count",)

    def __init__(
        self,
        boost_count: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ) -> None:
        super().__init__(api_kwargs=api_kwargs)
        self.boost_count: int = boost_count
        self._id_attrs = (self.boost_count,)

        self._freeze()
