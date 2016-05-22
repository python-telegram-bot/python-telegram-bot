#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains a object that represents a Telegram Video."""

from telegram import PhotoSize, TelegramObject


class Video(TelegramObject):
    """This object represents a Telegram Video.

    Attributes:
        file_id (str):
        width (int):
        height (int):
        duration (int):
        thumb (:class:`telegram.PhotoSize`):
        mime_type (str):
        file_size (int):

    Args:
        file_id (str):
        width (int):
        height (int):
        duration (int):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        thumb (Optional[:class:`telegram.PhotoSize`]):
        mime_type (Optional[str]):
        file_size (Optional[int]):
    """

    def __init__(self, file_id, width, height, duration, **kwargs):
        # Required
        self.file_id = str(file_id)
        self.width = int(width)
        self.height = int(height)
        self.duration = int(duration)
        # Optionals
        self.thumb = kwargs.get('thumb')
        self.mime_type = str(kwargs.get('mime_type', ''))
        self.file_size = int(kwargs.get('file_size', 0))

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.Video:
        """
        if not data:
            return None

        data['thumb'] = PhotoSize.de_json(data.get('thumb'))

        return Video(**data)
