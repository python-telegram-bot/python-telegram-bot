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
"""This module contains objects that represents stickers."""

from telegram import PhotoSize, TelegramObject


class Sticker(TelegramObject):
    """This object represents a Telegram Sticker.

    Attributes:
        file_id (str):
        width (int):
        height (int):
        thumb (:class:`telegram.PhotoSize`):
        emoji (str):
        file_size (int):

    Args:
        file_id (str):
        width (int):
        height (int):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        thumb (Optional[:class:`telegram.PhotoSize`]):
        emoji (Optional[str]):
        file_size (Optional[int]):
    """

    def __init__(self,
                 file_id,
                 width,
                 height,
                 thumb=None,
                 emoji=None,
                 file_size=None,
                 set_name=None,
                 mask_position=None,
                 **kwargs):
        # Required
        self.file_id = str(file_id)
        self.width = int(width)
        self.height = int(height)
        # Optionals
        self.thumb = thumb
        self.emoji = emoji
        self.file_size = file_size
        self.set_name = set_name
        self.mask_position = mask_position

        self._id_attrs = (self.file_id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Sticker:
        """
        if not data:
            return None

        data = super(Sticker, Sticker).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)
        data['mask_position'] = MaskPosition.de_json(data.get('mask_position'), bot)

        return Sticker(**data)

    @staticmethod
    def de_list(data, bot):
        if not data:
            return list()

        stickers = list()
        for sticker in data:
            stickers.append(Sticker.de_json(sticker, bot))

        return stickers


class StickerSet(TelegramObject):
    def __init__(self, name, title, is_mask, stickers):
        self.name = name
        self.title = title
        self.is_mask = is_mask
        self.stickers = stickers

        self._id_attrs = (self.name,)

    @staticmethod
    def de_json(data, bot):
        if not data:
            return None

        data = super(StickerSet, StickerSet).de_json(data, bot)

        data['stickers'] = Sticker.de_list(data.get('stickers'), bot)

        return StickerSet(**data)


class MaskPosition(TelegramObject):
    FOREHEAD = 'forehead'
    EYES = 'eyes'
    MOUTH = 'mouth'
    CHIN = 'chin'

    def __init__(self, point, x_shift, y_shift, zoom):
        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.zoom = zoom

    @staticmethod
    def de_json(data, bot):
        if data is None:
            return None

        return MaskPosition(**data)
