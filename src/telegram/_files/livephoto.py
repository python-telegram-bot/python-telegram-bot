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
"""This module contains an object that represents a Telegram LivePhoto."""

import datetime as dtm

from telegram._files._basemedium import _BaseMedium
from telegram._files.photosize import PhotoSize
from telegram._utils.argumentparsing import parse_sequence_arg, to_timedelta
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class LivePhoto(_BaseMedium):
    """
    This object represents a live photo.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    .. versionadded:: 22.8

    Args:
        file_id (:obj:`str`): Identifier for the video file which can be used to download or reuse
            the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Video width as defined by the sender.
        height (:obj:`int`): Video height as defined by the sender.
        duration (:obj:`int` | :class:`datetime.timedelta`): Duration of the video
            in seconds as defined by the sender.
        photo (Sequence[:obj:`telegram.PhotoSize`], optional): Available sizes of the corresponding
            static photo.
        mime_type (:obj:`str`, optional): MIME type of a file as defined by the sender.
        file_size (:obj:`int`, optional): File size in bytes.

    Attributes:
        file_id (:obj:`str`): Identifier for the video file which can be used to download or reuse
            the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Video width as defined by the sender.
        height (:obj:`int`): Video height as defined by the sender.
        duration (:class:`datetime.timedelta`): Duration of the video
            in seconds as defined by the sender.
        photo (tuple[:obj:`telegram.PhotoSize`]): Optional. Available sizes of the corresponding
            static photo.
        mime_type (:obj:`str`): Optional. MIME type of a file as defined by the sender.
        file_size (:obj:`int`): Optional. File size in bytes.

    """

    # Required
    width: int = tg_field()
    height: int = tg_field()
    duration: dtm.timedelta = tg_field(converter=to_timedelta)
    # Optional
    photo: tuple[PhotoSize, ...] = tg_field(default=None, converter=parse_sequence_arg)
    mime_type: str | None = tg_field(default=None)
    file_size: int | None = tg_field(default=None)
