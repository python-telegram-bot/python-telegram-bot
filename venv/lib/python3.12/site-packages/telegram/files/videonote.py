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
"""This module contains an object that represents a Telegram VideoNote."""

from typing import TYPE_CHECKING, Optional, Any

from telegram import PhotoSize, TelegramObject
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot, File


class VideoNote(TelegramObject):
    """This object represents a video message (available in Telegram apps as of v.4.0).

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        length (:obj:`int`): Video width and height (diameter of the video message) as defined
            by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`, optional): Video thumbnail.
        file_size (:obj:`int`, optional): File size.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        file_id (:obj:`str`): Identifier for this file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        length (:obj:`int`): Video width and height as defined by sender.
        duration (:obj:`int`): Duration of the video in seconds as defined by sender.
        thumb (:class:`telegram.PhotoSize`): Optional. Video thumbnail.
        file_size (:obj:`int`): Optional. File size.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """

    __slots__ = (
        'bot',
        'length',
        'file_id',
        'file_size',
        'thumb',
        'duration',
        'file_unique_id',
        '_id_attrs',
    )

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        length: int,
        duration: int,
        thumb: PhotoSize = None,
        file_size: int = None,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        # Required
        self.file_id = str(file_id)
        self.file_unique_id = str(file_unique_id)
        self.length = int(length)
        self.duration = int(duration)
        # Optionals
        self.thumb = thumb
        self.file_size = file_size
        self.bot = bot

        self._id_attrs = (self.file_unique_id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['VideoNote']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return cls(bot=bot, **data)

    def get_file(
        self, timeout: ODVInput[float] = DEFAULT_NONE, api_kwargs: JSONDict = None
    ) -> 'File':
        """Convenience wrapper over :attr:`telegram.Bot.get_file`

        For the documentation of the arguments, please see :meth:`telegram.Bot.get_file`.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.error.TelegramError`

        """
        return self.bot.get_file(file_id=self.file_id, timeout=timeout, api_kwargs=api_kwargs)
