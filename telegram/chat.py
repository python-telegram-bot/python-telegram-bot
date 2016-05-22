#!/usr/bin/env python
# pylint: disable=C0103,W0622
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains a object that represents a Telegram Chat."""

from telegram import TelegramObject


class Chat(TelegramObject):
    """This object represents a Telegram Chat.

    Attributes:
        id (int):
        type (str): Can be 'private', 'group', 'supergroup' or 'channel'
        title (str): Title, for channels and group chats
        username (str): Username, for private chats and channels if available
        first_name (str): First name of the other party in a private chat
        last_name (str): Last name of the other party in a private chat

    Args:
        id (int):
        type (str):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        type (Optional[str]):
    """

    def __init__(self, id, type, **kwargs):
        # Required
        self.id = int(id)
        self.type = type
        # Optionals
        self.title = kwargs.get('title', '')
        self.username = kwargs.get('username', '')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.Chat:
        """
        if not data:
            return None

        return Chat(**data)
