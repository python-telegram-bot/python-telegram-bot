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


from .replymarkup import ReplyMarkup


class ReplyKeyboardMarkup(ReplyMarkup):
    def __init__(self,
                 keyboard,
                 resize_keyboard=None,
                 one_time_keyboard=None,
                 selective=None):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ReplyKeyboardMarkup(keyboard=data.get('keyboard', None),
                                   resize_keyboard=data.get(
                                       'resize_keyboard', None
                                       ),
                                   one_time_keyboard=data.get(
                                       'one_time_keyboard', None
                                       ),
                                   selective=data.get('selective', None))

    def to_dict(self):
        data = {'keyboard': self.keyboard}
        if self.resize_keyboard:
            data['resize_keyboard'] = self.resize_keyboard
        if self.one_time_keyboard:
            data['one_time_keyboard'] = self.one_time_keyboard
        if self.selective:
            data['selective'] = self.selective
        return data
