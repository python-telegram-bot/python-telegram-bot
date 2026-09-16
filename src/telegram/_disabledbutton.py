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
"""This module contains an object that represents a Telegram DisabledButton."""

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class DisabledButton(TelegramObject):
    """This object represents a button that does nothing and is visually disabled.

    .. versionadded:: 22.9
    """

    __slots__ = ()

    def __init__(self, *, api_kwargs: JSONDict | None = None):
        super().__init__(api_kwargs=api_kwargs)
        self._id_attrs = (self.__class__.__name__,)
        self._freeze()
