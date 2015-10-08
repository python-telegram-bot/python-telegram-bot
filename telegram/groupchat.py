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

"""This module contains a object that represents a Telegram GroupChat"""

from telegram import TelegramObject


class GroupChat(TelegramObject):
    """This object represents a Telegram GroupChat.

    Attributes:
        id (int):
        title (str):
        type (str):

    Args:
        id (int):
        title (str):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        type (Optional[str]):
    """

    def __init__(self,
                 id,
                 title,
                 **kwargs):
        # Required
        self.id = int(id)
        self.title = title
        # Optionals
        self.type = kwargs.get('type', '')

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.GroupChat:
        """
        if not data:
            return None

        return GroupChat(**data)
