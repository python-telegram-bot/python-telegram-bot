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


class ForceReply(ReplyMarkup):
    def __init__(self,
                 force_reply=True,
                 selective=None):
        self.force_reply = force_reply
        self.selective = selective

    @staticmethod
    def de_json(data):
        return ForceReply(force_reply=data.get('force_reply', None),
                          selective=data.get('selective', None))

    def to_dict(self):
        data = {'force_reply': self.force_reply}
        if self.selective:
            data['selective'] = self.selective
        return data
