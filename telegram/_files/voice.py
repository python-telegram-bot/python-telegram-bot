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
"""This module contains an object that represents a Telegram Voice."""
import datetime as dtm
from typing import TYPE_CHECKING, Optional, Union

from telegram._files._basemedium import _BaseMedium
from telegram._utils.argumentparsing import parse_period_arg
from telegram._utils.datetime import get_timedelta_value
from telegram._utils.types import JSONDict, TimePeriod

if TYPE_CHECKING:
    from telegram import Bot


class Voice(_BaseMedium):
    """This object represents a voice note.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        duration (:obj:`int` | :class:`datetime.timedelta`): Duration of the audio in
            seconds as defined by the sender.

            .. versionchanged:: NEXT.VERSION
                |time-period-input|
        mime_type (:obj:`str`, optional): MIME type of the file as defined by the sender.
        file_size (:obj:`int`, optional): File size in bytes.

    Attributes:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        duration (:obj:`int` | :class:`datetime.timedelta`): Duration of the audio in seconds as
            defined by the sender.

            .. deprecated:: NEXT.VERSION
                |time-period-int-deprecated|
        mime_type (:obj:`str`): Optional. MIME type of the file as defined by the sender.
        file_size (:obj:`int`): Optional. File size in bytes.

    """

    __slots__ = ("_duration", "mime_type")

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        duration: TimePeriod,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_size=file_size,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            # Required
            self._duration: dtm.timedelta = parse_period_arg(duration)  # type: ignore[assignment]
            # Optional
            self.mime_type: Optional[str] = mime_type

    @property
    def duration(self) -> Union[int, dtm.timedelta]:
        value = get_timedelta_value(self._duration, attribute="duration")
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return value  # type: ignore[return-value]

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "Voice":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["duration"] = dtm.timedelta(seconds=s) if (s := data.get("duration")) else None

        return super().de_json(data=data, bot=bot)

    def to_dict(self, recursive: bool = True) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        out = super().to_dict(recursive)
        if self._duration is not None:
            seconds = self._duration.total_seconds()
            out["duration"] = int(seconds) if seconds.is_integer() else seconds
        elif not recursive:
            out["duration"] = self._duration
        return out
