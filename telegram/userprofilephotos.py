#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains an object that represents a Telegram UserProfilePhotos."""

from typing import TYPE_CHECKING, Any, List, Optional

from telegram import PhotoSize, TelegramObject
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class UserProfilePhotos(TelegramObject):
    """This object represent a user's profile pictures.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`total_count` and :attr:`photos` are equal.

    Args:
        total_count (:obj:`int`): Total number of profile pictures the target user has.
        photos (List[List[:class:`telegram.PhotoSize`]]): Requested profile pictures (in up to 4
            sizes each).

    Attributes:
        total_count (:obj:`int`): Total number of profile pictures.
        photos (List[List[:class:`telegram.PhotoSize`]]): Requested profile pictures.

    """

    def __init__(self, total_count: int, photos: List[List[PhotoSize]], **_kwargs: Any):
        # Required
        self.total_count = int(total_count)
        self.photos = photos

        self._id_attrs = (self.total_count, self.photos)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['UserProfilePhotos']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['photos'] = [PhotoSize.de_list(photo, bot) for photo in data['photos']]

        return cls(**data)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['photos'] = []
        for photo in self.photos:
            data['photos'].append([x.to_dict() for x in photo])

        return data

    def __hash__(self) -> int:
        return hash(tuple(tuple(p for p in photo) for photo in self.photos))
