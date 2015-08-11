#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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


from telegram import TelegramObject


class Sticker(TelegramObject):
    def __init__(self,
                 file_id,
                 width,
                 height,
                 thumb=None,
                 file_size=None):
        self.file_id = file_id
        self.width = width
        self.height = height
        self.thumb = thumb
        self.file_size = file_size

    @staticmethod
    def de_json(data):
        if 'thumb' in data:
            from telegram import PhotoSize
            thumb = PhotoSize.de_json(data['thumb'])
        else:
            thumb = None

        return Sticker(file_id=data.get('file_id', None),
                       width=data.get('width', None),
                       height=data.get('height', None),
                       thumb=thumb,
                       file_size=data.get('file_size', None))

    def to_dict(self):
        data = {'file_id': self.file_id,
                'width': self.width,
                'height': self.height,
                'thumb': self.thumb.to_dict()}
        if self.file_size:
            data['file_size'] = self.file_size
        return data
