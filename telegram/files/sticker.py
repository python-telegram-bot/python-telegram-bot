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
    """This object represents a sticker.

    Attributes:
        file_id (:obj:`str`): Unique identifier for this file.
        width (:obj:`int`): Sticker width.
        height (:obj:`int`): Sticker height.
        thumb (:class:`telegram.PhotoSize`): Optional. Sticker thumbnail in the .webp or .jpg
            format.
        emoji (:obj:`str`): Optional. Emoji associated with the sticker.
        set_name (:obj:`str`): Optional. Name of the sticker set to which the sticker belongs.
        mask_position (:class:`telegram.MaskPosition`): Optional. For mask stickers, the position
            where the mask should be placed.
        file_size (:obj:`int`): Optional. File size.

    Args:
        file_id (:obj:`str`): Unique identifier for this file.
        width (:obj:`int`): Sticker width.
        height (:obj:`int`): Sticker height.
        thumb (:class:`telegram.PhotoSize`, optional): Sticker thumbnail in the .webp or .jpg
            format.
        emoji (:obj:`str`, optional): Emoji associated with the sticker
        set_name (:obj:`str`, optional): Name of the sticker set to which the sticker
            belongs.
        mask_position (:class:`telegram.MaskPosition`, optional): For mask stickers, the
            position where the mask should be placed.
        file_size (:obj:`int`, optional): File size.
        **kwargs (obj:`dict`): Arbitrary keyword arguments.

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

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(Sticker, cls).de_json(data, bot)

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)
        data['mask_position'] = MaskPosition.de_json(data.get('mask_position'), bot)

        return cls(**data)

    @classmethod
    def de_list(cls, data, bot):
        if not data:
            return list()

        return [cls.de_json(d, bot) for d in data]


class StickerSet(TelegramObject):
    """This object represents a sticker set.

    Attributes:
        name (:obj:`str`): Sticker set name.
        title (:obj:`str`): Sticker set title.
        contains_masks (:obj:`bool`): True, if the sticker set contains masks.
        stickers (List[:class:`telegram.Sticker`]): List of all set stickers.

    Args:
        name (:obj:`str`): Sticker set name.
        title (:obj:`str`): Sticker set title.
        contains_masks (:obj:`bool`): True, if the sticker set contains masks.
        stickers (List[:class:`telegram.Sticker`]): List of all set stickers.

    """

    def __init__(self, name, title, contains_masks, stickers, bot=None, **kwargs):
        self.name = name
        self.title = title
        self.contains_masks = contains_masks
        self.stickers = stickers

        self._id_attrs = (self.name,)

    @staticmethod
    def de_json(data, bot):
        if not data:
            return None

        data = super(StickerSet, StickerSet).de_json(data, bot)

        data['stickers'] = Sticker.de_list(data.get('stickers'), bot)

        return StickerSet(bot=bot, **data)

    def to_dict(self):
        data = super(StickerSet, self).to_dict()

        data['stickers'] = [s.to_dict() for s in data.get('stickers')]

        return data


class MaskPosition(TelegramObject):
    """This object describes the position on faces where a mask should be placed by default.

    Attributes:
        point (:obj:`str`): The part of the face relative to which the mask should be placed.
        x_shift (:obj:`float`): Shift by X-axis measured in widths of the mask scaled to the face
            size, from left to right.
        y_shift (:obj:`float`): Shift by Y-axis measured in heights of the mask scaled to the face
            size, from top to bottom.
        scale (:obj:`float`): Mask scaling coefficient. For example, 2.0 means double size.

    Notes:
        :attr:`type` should be one of the following: `forehead`, `eyes`, `mouth` or `chin`. You can
        use the classconstants for those.

    Args:
        point (:obj:`str`): The part of the face relative to which the mask should be placed.
        x_shift (:obj:`float`): Shift by X-axis measured in widths of the mask scaled to the face
            size, from left to right. For example, choosing -1.0 will place mask just to the left
            of the default mask position.
        y_shift (:obj:`float`): Shift by Y-axis measured in heights of the mask scaled to the face
            size, from top to bottom. For example, 1.0 will place the mask just below the default
            mask position.
        scale (:obj:`float`): Mask scaling coefficient. For example, 2.0 means double size.

    """
    FOREHEAD = 'forehead'
    """:obj:`str`: 'forehead'"""
    EYES = 'eyes'
    """:obj:`str`: 'eyes'"""
    MOUTH = 'mouth'
    """:obj:`str`: 'mouth'"""
    CHIN = 'chin'
    """:obj:`str`: 'chin'"""

    def __init__(self, point, x_shift, y_shift, scale, **kwargs):
        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.scale = scale

    @classmethod
    def de_json(cls, data, bot):
        if data is None:
            return None

        return cls(**data)
