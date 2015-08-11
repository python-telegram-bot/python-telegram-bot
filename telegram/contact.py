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


class Contact(TelegramObject):
    def __init__(self,
                 phone_number,
                 first_name,
                 last_name=None,
                 user_id=None):
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

    @staticmethod
    def de_json(data):
        return Contact(phone_number=data.get('phone_number', None),
                       first_name=data.get('first_name', None),
                       last_name=data.get('last_name', None),
                       user_id=data.get('user_id', None))

    def to_dict(self):
        data = {'phone_number': self.phone_number,
                'first_name': self.first_name}
        if self.last_name:
            data['last_name'] = self.last_name
        if self.user_id:
            data['user_id'] = self.user_id
        return data
