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
"""This module contains a object that represents a Telegram PhotoSize."""

from telegram import TelegramObject


class PhotoSize(TelegramObject):
    """This object represents a Telegram PhotoSize.

    Attributes:
        file_id (str):
        width (int):
        height (int):
        file_size (int):

    Args:
        file_id (str):
        width (int):
        height (int):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        file_size (Optional[int]):
    """

    def __init__(self, file_id, width, height, **kwargs):
        # Required
        self.file_id = str(file_id)
        self.width = int(width)
        self.height = int(height)
        # Optionals
        self.file_size = int(kwargs.get('file_size', 0))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self.file_id == other.file_id and self.width == other.width and
                self.height == other.height and self.file_size == other.file_size)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.PhotoSize:
        """
        if not data:
            return None

        return PhotoSize(**data)

    @staticmethod
    def de_list(data):
        """
        Args:
            data (list):

        Returns:
            List<telegram.PhotoSize>:
        """
        if not data:
            return []

        photos = list()
        for photo in data:
            photos.append(PhotoSize.de_json(photo))

        return photos
