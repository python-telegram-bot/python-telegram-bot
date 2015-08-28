#!/usr/bin/env python
# pylint: disable=C0103,W0622
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

"""This module contains a object that represents a Telegram User"""

from telegram import TelegramObject


class User(TelegramObject):
    """This object represents a Telegram Sticker.

    Attributes:
        id (int):
        first_name (str):
        last_name (str):
        username (str):

    Args:
        id (int):
        first_name (str):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        last_name (Optional[str]):
        username (Optional[str]):
    """

    def __init__(self,
                 id,
                 first_name,
                 **kwargs):
        # Required
        self.id = int(id)
        self.first_name = first_name
        # Optionals
        self.last_name = kwargs.get('last_name', '')
        self.username = kwargs.get('username', '')

    @property
    def name(self):
        """str: """
        if self.username:
            return '@%s' % self.username
        if self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        return self.first_name

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.User:
        """
        if not data:
            return None

        user = dict()

        # Required
        user['id'] = data['id']
        user['first_name'] = data['first_name']
        # Optionals
        user['last_name'] = data.get('last_name')
        user['username'] = data.get('username')

        return User(**user)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = dict()

        # Required
        data['id'] = self.id
        data['first_name'] = self.first_name
        # Optionals
        if self.last_name:
            data['last_name'] = self.last_name
        if self.username:
            data['username'] = self.username

        return data
