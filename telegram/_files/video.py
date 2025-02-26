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
"""This module contains an object that represents a Telegram Video."""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional

from telegram._files._basethumbedmedium import _BaseThumbedMedium
from telegram._files.photosize import PhotoSize
from telegram._utils.argumentparsing import de_list_optional, parse_sequence_arg
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class Video(_BaseThumbedMedium):
    """This object represents a video file.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    .. versionchanged:: 20.5
      |removed_thumb_note|

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Video width as defined by the sender.
        height (:obj:`int`): Video height as defined by the sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by the sender.
        file_name (:obj:`str`, optional): Original filename as defined by the sender.
        mime_type (:obj:`str`, optional): MIME type of a file as defined by the sender.
        file_size (:obj:`int`, optional): File size in bytes.
        thumbnail (:class:`telegram.PhotoSize`, optional): Video thumbnail.

            .. versionadded:: 20.2
        cover (Sequence[:class:`telegram.PhotoSize`], optional): Available sizes of the cover of
            the video in the message.

            .. versionadded:: NEXT.VERSION
        start_timestamp (:obj:`int`, optional): Timestamp in seconds from which the video
            will play in the message
            .. versionadded:: NEXT.VERSION

    Attributes:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Video width as defined by the sender.
        height (:obj:`int`): Video height as defined by the sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by the sender.
        file_name (:obj:`str`): Optional. Original filename as defined by the sender.
        mime_type (:obj:`str`): Optional. MIME type of a file as defined by the sender.
        file_size (:obj:`int`): Optional. File size in bytes.
        thumbnail (:class:`telegram.PhotoSize`): Optional. Video thumbnail.

            .. versionadded:: 20.2
        cover (tuple[:class:`telegram.PhotoSize`]): Optional, Available sizes of the cover of
            the video in the message.

            .. versionadded:: NEXT.VERSION
        start_timestamp (:obj:`int`): Optional, Timestamp in seconds from which the video
            will play in the message
            .. versionadded:: NEXT.VERSION
    """

    __slots__ = (
        "cover",
        "duration",
        "file_name",
        "height",
        "mime_type",
        "start_timestamp",
        "width",
    )

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        file_name: Optional[str] = None,
        thumbnail: Optional[PhotoSize] = None,
        cover: Optional[Sequence[PhotoSize]] = None,
        start_timestamp: Optional[int] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_size=file_size,
            thumbnail=thumbnail,
            api_kwargs=api_kwargs,
        )
        with self._unfrozen():
            # Required
            self.width: int = width
            self.height: int = height
            self.duration: int = duration
            # Optional
            self.mime_type: Optional[str] = mime_type
            self.file_name: Optional[str] = file_name
            self.cover: Optional[Sequence[PhotoSize]] = parse_sequence_arg(cover)
            self.start_timestamp: Optional[int] = start_timestamp

    @classmethod
    def de_json(cls, data: JSONDict, bot: Optional["Bot"] = None) -> "Video":
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        data["cover"] = de_list_optional(data.get("cover"), PhotoSize, bot)

        return super().de_json(data=data, bot=bot)
