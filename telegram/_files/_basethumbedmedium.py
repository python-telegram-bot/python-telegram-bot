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
"""Common base class for media objects with thumbnails"""
from typing import TYPE_CHECKING, Optional, Type, TypeVar

from telegram._files._basemedium import _BaseMedium
from telegram._files.photosize import PhotoSize
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot

# pylint: disable=invalid-name
ThumbedMT_co = TypeVar("ThumbedMT_co", bound="_BaseThumbedMedium", covariant=True)


class _BaseThumbedMedium(_BaseMedium):
    """
    Base class for objects representing the various media file types that may include a thumbnail.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`, optional): File size.
        thumb (:class:`telegram.PhotoSize`, optional): Thumbnail as defined by sender.

    Attributes:
        file_id (:obj:`str`): File identifier.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        file_size (:obj:`int`): Optional. File size.
        thumb (:class:`telegram.PhotoSize`): Optional. Thumbnail as defined by sender.


    """

    __slots__ = ("thumb",)

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        file_size: int = None,
        thumb: PhotoSize = None,
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_size=file_size,
            api_kwargs=api_kwargs,
        )
        self.thumb: Optional[PhotoSize] = thumb

    @classmethod
    def de_json(
        cls: Type[ThumbedMT_co], data: Optional[JSONDict], bot: "Bot"
    ) -> Optional[ThumbedMT_co]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        # In case this wasn't already done by the subclass
        if not isinstance(data.get("thumb"), PhotoSize):
            data["thumb"] = PhotoSize.de_json(data.get("thumb"), bot)

        return super().de_json(data=data, bot=bot)
