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
"""This module contains an object that represents a Telegram Audio."""

import datetime as dtm

from telegram._files._basemedium import _BaseMedium
from telegram._files.photosize import PhotoSize
from telegram._utils.argumentparsing import to_timedelta
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.datetime import get_timedelta_value


@tg_dataclass()
class Audio(_BaseMedium):
    """This object represents an audio file to be treated as music by the Telegram clients.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    .. versionchanged:: 20.5
      |removed_thumb_note|


    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which is supposed to be
            the same over time and for different bots. Can't be used to download or reuse the file.
        duration (:obj:`int` | :class:`datetime.timedelta`): Duration of the audio in
            seconds as defined by the sender.

            .. versionchanged:: v22.2
                |time-period-input|
        performer (:obj:`str`, optional): Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`, optional): Title of the audio as defined by the sender or by audio tags.
        file_name (:obj:`str`, optional): Original filename as defined by the sender.
        mime_type (:obj:`str`, optional): MIME type of the file as defined by the sender.
        file_size (:obj:`int`, optional): File size in bytes.
        thumbnail (:class:`telegram.PhotoSize`, optional): Thumbnail of the album cover to
            which the music file belongs.

            .. versionadded:: 20.2

    Attributes:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which is supposed to be
            the same over time and for different bots. Can't be used to download or reuse the file.
        duration (:obj:`int` | :class:`datetime.timedelta`): Duration of the audio in seconds as
            defined by the sender.

            .. deprecated:: v22.2
                |time-period-int-deprecated|
        performer (:obj:`str`): Optional. Performer of the audio as defined by the sender or by
            audio tags.
        title (:obj:`str`): Optional. Title of the audio as defined by the sender or by audio tags.
        file_name (:obj:`str`): Optional. Original filename as defined by the sender.
        mime_type (:obj:`str`): Optional. MIME type of the file as defined by the sender.
        file_size (:obj:`int`): Optional. File size in bytes.
        thumbnail (:class:`telegram.PhotoSize`): Optional. Thumbnail of the album cover to
            which the music file belongs.

            .. versionadded:: 20.2


    """

    # Required
    _duration: dtm.timedelta = tg_field(alias="duration", converter=to_timedelta)
    # Optional
    performer: str | None = tg_field(default=None)
    title: str | None = tg_field(default=None)
    mime_type: str | None = tg_field(default=None)
    file_size: int | None = tg_field(default=None)
    file_name: str | None = tg_field(default=None)
    thumbnail: PhotoSize | None = tg_field(default=None)

    @property
    def duration(self) -> int | dtm.timedelta:
        return get_timedelta_value(  # type: ignore[return-value]
            self._duration, attribute="duration"
        )
