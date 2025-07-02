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
"""This module contains an object that represents a Telegram CallbackGame."""
from typing import Optional, TYPE_CHECKING

from telegram import TelegramObject
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class CallbackGame(TelegramObject):
    """A placeholder, currently holds no information. Use BotFather to set up your game."""

    __slots__ = ()

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['CallbackGame']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        if data is None:
            return None
        return cls()
