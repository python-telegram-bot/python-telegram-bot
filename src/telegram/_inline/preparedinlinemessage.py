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
"""This module contains an object that represents a Telegram Prepared inline Message."""

import datetime as dtm

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class PreparedInlineMessage(TelegramObject):
    """Describes an inline message to be sent by a user of a Mini App.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    .. versionadded:: 21.8

    Args:
        id (:obj:`str`): Unique identifier of the prepared message
        expiration_date (:class:`datetime.datetime`): Expiration date of the prepared message.
            Expired prepared messages can no longer be used.
            |datetime_localization|

    Attributes:
        id (:obj:`str`): Unique identifier of the prepared message
        expiration_date (:class:`datetime.datetime`): Expiration date of the prepared message.
            Expired prepared messages can no longer be used.
            |datetime_localization|
    """

    # Required
    id: str = tg_field(compare=True)
    expiration_date: dtm.datetime = tg_field()
