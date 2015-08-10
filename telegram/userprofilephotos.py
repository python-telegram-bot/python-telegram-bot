#!/usr/bin/env python

"""
    A library that provides a Python interface to the Telegram Bot API
    Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser Public License for more details.

    You should have received a copy of the GNU Lesser Public License
    along with this program.  If not, see [http://www.gnu.org/licenses/].
"""


from telegram import TelegramObject


class UserProfilePhotos(TelegramObject):
    def __init__(self,
                 total_count,
                 photos):
        self.total_count = total_count
        self.photos = photos

    @staticmethod
    def de_json(data):
        if 'photos' in data:
            from telegram import PhotoSize
            photos = []
            for photo in data['photos']:
                photos.append([PhotoSize.de_json(x) for x in photo])
        else:
            photos = None

        return UserProfilePhotos(total_count=data.get('total_count', None),
                                 photos=photos)

    def to_dict(self):
        data = {}
        if self.total_count:
            data['total_count'] = self.total_count
        if self.photos:
            data['photos'] = []
            for photo in self.photos:
                data['photos'].append([x.to_dict() for x in photo])
        return data
