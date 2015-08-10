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


class Location(TelegramObject):
    def __init__(self,
                 longitude,
                 latitude):
        self.longitude = longitude
        self.latitude = latitude

    @staticmethod
    def de_json(data):
        return Location(longitude=data.get('longitude', None),
                        latitude=data.get('latitude', None))

    def to_dict(self):
        data = {'longitude': self.longitude,
                'latitude': self.latitude}
        return data
