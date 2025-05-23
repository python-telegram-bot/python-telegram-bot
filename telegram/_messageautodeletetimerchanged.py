#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
deletion.
"""

import datetime as dtm
from typing import TYPE_CHECKING, Optional, Union

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_period_arg
from telegram._utils.datetime import get_timedelta_value
from telegram._utils.types import JSONDict, TimePeriod

if TYPE_CHECKING:
    from telegram import Bot


class MessageAutoDeleteTimerChanged(TelegramObject):
    """This object represents a service message about a change in auto-delete timer settings.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`message_auto_delete_time` is equal.

    .. versionadded:: 13.4

    Args:
        message_auto_delete_time (:obj:`int` | :class:`datetime.timedelta`): New auto-delete time
            for messages in the chat.

            .. versionchanged:: NEXT.VERSION
                |time-period-input|

    Attributes:
        message_auto_delete_time (:obj:`int` | :class:`datetime.timedelta`): New auto-delete time
            for messages in the chat.

            .. deprecated:: NEXT.VERSION
                |time-period-int-deprecated|

    """

    __slots__ = ("_message_auto_delete_time",)

    def __init__(
        self,
        message_auto_delete_time: TimePeriod,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self._message_auto_delete_time: dtm.timedelta = parse_period_arg(
            message_auto_delete_time
        )  # type: ignore[assignment]

        self._id_attrs = (self.message_auto_delete_time,)

        self._freeze()

    @property
    def message_auto_delete_time(self) -> Union[int, dtm.timedelta]:
        value = get_timedelta_value(
            self._message_auto_delete_time, attribute="message_auto_delete_time"
        )
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return value  # type: ignore[return-value]

    @classmethod
    def de_json(
        cls, data: JSONDict, bot: Optional["Bot"] = None
    ) -> "MessageAutoDeleteTimerChanged":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)
        data["message_auto_delete_time"] = (
            dtm.timedelta(seconds=s) if (s := data.get("message_auto_delete_time")) else None
        )

        return super().de_json(data=data, bot=bot)

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        out = super().to_dict(recursive)
        if self._message_auto_delete_time is not None:
            seconds = self._message_auto_delete_time.total_seconds()
            out["message_auto_delete_time"] = int(seconds) if seconds.is_integer() else seconds
        elif not recursive:
            out["message_auto_delete_time"] = self._message_auto_delete_time
        return out
