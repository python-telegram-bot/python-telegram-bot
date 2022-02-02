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
"""This module contains objects that represents stickers."""

from typing import TYPE_CHECKING, Any, List, Optional, ClassVar

from telegram import PhotoSize, TelegramObject, constants
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot, File


class Sticker(TelegramObject):
    """This object represents a sticker.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`file_unique_id` is equal.

    Note:
        As of v13.11 ``is_video`` is a required argument and therefore the order of the
        arguments had to be changed. Use keyword arguments to make sure that the arguments are
        passed correctly.

    Args:
        file_id (:obj:`str`): Identifier for this file, which can be used to download
            or reuse the file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Sticker width.
        height (:obj:`int`): Sticker height.
        is_animated (:obj:`bool`): :obj:`True`, if the sticker is animated.
        is_video (:obj:`bool`): :obj:`True`, if the sticker is a video sticker.

            .. versionadded:: 13.11
        thumb (:class:`telegram.PhotoSize`, optional): Sticker thumbnail in the .WEBP or .JPG
            format.
        emoji (:obj:`str`, optional): Emoji associated with the sticker
        set_name (:obj:`str`, optional): Name of the sticker set to which the sticker
            belongs.
        mask_position (:class:`telegram.MaskPosition`, optional): For mask stickers, the
            position where the mask should be placed.
        file_size (:obj:`int`, optional): File size.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        file_id (:obj:`str`): Identifier for this file.
        file_unique_id (:obj:`str`): Unique identifier for this file, which
            is supposed to be the same over time and for different bots.
            Can't be used to download or reuse the file.
        width (:obj:`int`): Sticker width.
        height (:obj:`int`): Sticker height.
        is_animated (:obj:`bool`): :obj:`True`, if the sticker is animated.
        is_video (:obj:`bool`): :obj:`True`, if the sticker is a video sticker.

            .. versionadded:: 13.11
        thumb (:class:`telegram.PhotoSize`): Optional. Sticker thumbnail in the .webp or .jpg
            format.
        emoji (:obj:`str`): Optional. Emoji associated with the sticker.
        set_name (:obj:`str`): Optional. Name of the sticker set to which the sticker belongs.
        mask_position (:class:`telegram.MaskPosition`): Optional. For mask stickers, the position
            where the mask should be placed.
        file_size (:obj:`int`): Optional. File size.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    """

    __slots__ = (
        'bot',
        'width',
        'file_id',
        'is_animated',
        'is_video',
        'file_size',
        'thumb',
        'set_name',
        'mask_position',
        'height',
        'file_unique_id',
        'emoji',
        '_id_attrs',
    )

    def __init__(
        self,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        is_animated: bool,
        is_video: bool,
        thumb: PhotoSize = None,
        emoji: str = None,
        file_size: int = None,
        set_name: str = None,
        mask_position: 'MaskPosition' = None,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        # Required
        self.file_id = str(file_id)
        self.file_unique_id = str(file_unique_id)
        self.width = int(width)
        self.height = int(height)
        self.is_animated = is_animated
        self.is_video = is_video
        # Optionals
        self.thumb = thumb
        self.emoji = emoji
        self.file_size = file_size
        self.set_name = set_name
        self.mask_position = mask_position
        self.bot = bot

        self._id_attrs = (self.file_unique_id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['Sticker']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)
        data['mask_position'] = MaskPosition.de_json(data.get('mask_position'), bot)

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


class StickerSet(TelegramObject):
    """This object represents a sticker set.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`name` is equal.

    Note:
        As of v13.11 ``is_video`` is a required argument and therefore the order of the
        arguments had to be changed. Use keyword arguments to make sure that the arguments are
        passed correctly.

    Args:
        name (:obj:`str`): Sticker set name.
        title (:obj:`str`): Sticker set title.
        is_animated (:obj:`bool`): :obj:`True`, if the sticker set contains animated stickers.
        is_video (:obj:`bool`): :obj:`True`, if the sticker set contains video stickers.

            .. versionadded:: 13.11
        contains_masks (:obj:`bool`): :obj:`True`, if the sticker set contains masks.
        stickers (List[:class:`telegram.Sticker`]): List of all set stickers.
        thumb (:class:`telegram.PhotoSize`, optional): Sticker set thumbnail in the ``.WEBP``,
            ``.TGS``, or ``.WEBM`` format.

    Attributes:
        name (:obj:`str`): Sticker set name.
        title (:obj:`str`): Sticker set title.
        is_animated (:obj:`bool`): :obj:`True`, if the sticker set contains animated stickers.
        is_video (:obj:`bool`): :obj:`True`, if the sticker set contains video stickers.

            .. versionadded:: 13.11
        contains_masks (:obj:`bool`): :obj:`True`, if the sticker set contains masks.
        stickers (List[:class:`telegram.Sticker`]): List of all set stickers.
        thumb (:class:`telegram.PhotoSize`): Optional. Sticker set thumbnail in the ``.WEBP``,
            ``.TGS`` or ``.WEBM`` format.

    """

    __slots__ = (
        'is_animated',
        'is_video',
        'contains_masks',
        'thumb',
        'title',
        'stickers',
        'name',
        '_id_attrs',
    )

    def __init__(
        self,
        name: str,
        title: str,
        is_animated: bool,
        contains_masks: bool,
        stickers: List[Sticker],
        is_video: bool,
        thumb: PhotoSize = None,
        **_kwargs: Any,
    ):
        self.name = name
        self.title = title
        self.is_animated = is_animated
        self.is_video = is_video
        self.contains_masks = contains_masks
        self.stickers = stickers
        # Optionals
        self.thumb = thumb

        self._id_attrs = (self.name,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['StickerSet']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        if not data:
            return None

        data['thumb'] = PhotoSize.de_json(data.get('thumb'), bot)
        data['stickers'] = Sticker.de_list(data.get('stickers'), bot)

        return cls(bot=bot, **data)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data['stickers'] = [s.to_dict() for s in data.get('stickers')]

        return data


class MaskPosition(TelegramObject):
    """This object describes the position on faces where a mask should be placed by default.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`point`, :attr:`x_shift`, :attr:`y_shift` and, :attr:`scale`
    are equal.

    Attributes:
        point (:obj:`str`): The part of the face relative to which the mask should be placed.
            One of ``'forehead'``, ``'eyes'``, ``'mouth'``, or ``'chin'``.
        x_shift (:obj:`float`): Shift by X-axis measured in widths of the mask scaled to the face
            size, from left to right.
        y_shift (:obj:`float`): Shift by Y-axis measured in heights of the mask scaled to the face
            size, from top to bottom.
        scale (:obj:`float`): Mask scaling coefficient. For example, 2.0 means double size.

    Note:
        :attr:`type` should be one of the following: `forehead`, `eyes`, `mouth` or `chin`. You can
        use the class constants for those.

    Args:
        point (:obj:`str`): The part of the face relative to which the mask should be placed.
            One of ``'forehead'``, ``'eyes'``, ``'mouth'``, or ``'chin'``.
        x_shift (:obj:`float`): Shift by X-axis measured in widths of the mask scaled to the face
            size, from left to right. For example, choosing -1.0 will place mask just to the left
            of the default mask position.
        y_shift (:obj:`float`): Shift by Y-axis measured in heights of the mask scaled to the face
            size, from top to bottom. For example, 1.0 will place the mask just below the default
            mask position.
        scale (:obj:`float`): Mask scaling coefficient. For example, 2.0 means double size.

    """

    __slots__ = ('point', 'scale', 'x_shift', 'y_shift', '_id_attrs')

    FOREHEAD: ClassVar[str] = constants.STICKER_FOREHEAD
    """:const:`telegram.constants.STICKER_FOREHEAD`"""
    EYES: ClassVar[str] = constants.STICKER_EYES
    """:const:`telegram.constants.STICKER_EYES`"""
    MOUTH: ClassVar[str] = constants.STICKER_MOUTH
    """:const:`telegram.constants.STICKER_MOUTH`"""
    CHIN: ClassVar[str] = constants.STICKER_CHIN
    """:const:`telegram.constants.STICKER_CHIN`"""

    def __init__(self, point: str, x_shift: float, y_shift: float, scale: float, **_kwargs: Any):
        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.scale = scale

        self._id_attrs = (self.point, self.x_shift, self.y_shift, self.scale)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['MaskPosition']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if data is None:
            return None

        return cls(**data)
