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
"""This module contains an object that represents a Telegram
UserProfilePhotos."""

from telegram import PhotoSize, TelegramObject


class UserProfilePhotos(TelegramObject):
    """This object represents a Telegram UserProfilePhotos.

    Attributes:
        total_count (int):
        photos (List[List[:class:`telegram.PhotoSize`]]):

    Args:
        total_count (int):
        photos (List[List[:class:`telegram.PhotoSize`]]):
    """

    def __init__(self, total_count, photos, **kwargs):
        # Required
        self.total_count = int(total_count)
        self.photos = photos

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.UserProfilePhotos:
        """
        if not data:
            return None

        data = super(UserProfilePhotos, UserProfilePhotos).de_json(data, bot)

        data['photos'] = [PhotoSize.de_list(photo, bot) for photo in data['photos']]

        return UserProfilePhotos(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(UserProfilePhotos, self).to_dict()

        data['photos'] = []
        for photo in self.photos:
            data['photos'].append([x.to_dict() for x in photo])

        return data
