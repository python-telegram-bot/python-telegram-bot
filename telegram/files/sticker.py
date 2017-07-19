#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains an object that represents a Telegram Sticker."""

from telegram import PhotoSize, TelegramObject


class Sticker(TelegramObject):
    """
    This object represents a sticker.

    Attributes:
        file_id (str): Unique identifier for this file.
        width (int): Sticker width.
        height (int): Sticker height.
        thumb (:class:`telegram.PhotoSize`): Optional. Sticker thumbnail in .webp or .jpg format.
        emoji (str): Optional. Emoji associated with the sticker.
        file_size (int): Optional. File size.

    Args:
        file_id (str): Unique identifier for this file.
        width (int): Sticker width.
        height (int): Sticker height.
        thumb (Optional[:class:`telegram.PhotoSize`]): Sticker thumbnail in .webp or .jpg format.
        emoji (Optional[str]): Emoji associated with the sticker.
        file_size (Optional[int]): File size.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, file_id, width, height, thumb=None, emoji=None, file_size=None, **kwargs):
        # Required
        self.file_id = str(file_id)
        self.width = int(width)
        self.height = int(height)
        # Optionals
        self.thumb = thumb
        self.emoji = emoji
        self.file_size = file_size

        self._id_attrs = (self.file_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (:class:`telegram.Bot`):

        Returns:
            :class:`telegram.Sticker`
        """

        if not data:
            return None

        data = super(Sticker, Sticker).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)

        return Sticker(**data)
