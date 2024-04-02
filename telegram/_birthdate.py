#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""This module contains an object that represents a Telegram Birthday."""
from typing import Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class Birthdate(TelegramObject):
    """
    This object represents a user's birthday.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`day`, and :attr:`month` are equal.

    .. versionadded:: NEXT.VERSION

    Args:
        day (:obj:`int`): Day of the user's birth; 1-31.
        month (:obj:`int`): Month of the user's birth; 1-12.
        year (:obj:`int`, optional): Year of the user's birth.

    Attributes:
        day (:obj:`int`): Day of the user's birth; 1-31.
        month (:obj:`int`): Month of the user's birth; 1-12.
        year (:obj:`int`): Optional. Year of the user's birth.

    """

    __slots__ = ("day", "month", "year")

    def __init__(
        self,
        day: int,
        month: int,
        year: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.day: int = day
        self.month: int = month
        # Optional
        self.year: Optional[int] = year

        self._id_attrs = (
            self.day,
            self.month,
        )

        self._freeze()
