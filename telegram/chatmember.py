#!/usr/bin/env python
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
"""This module contains an object that represents a Telegram ChatMember."""

from telegram import User, TelegramObject


class ChatMember(TelegramObject):
    """This object represents a Telegram ChatMember.

    Attributes:
        user (:class:`telegram.User`): Information about the user.
        status (str): The member's status in the chat. Can be 'creator', 'administrator', 'member',
            'left' or 'kicked'.

    Args:
        user (:class:`telegram.User`):
        status (str):
        **kwargs (dict): Arbitrary keyword arguments.

    """
    CREATOR = 'creator'
    ADMINISTRATOR = 'administrator'
    MEMBER = 'member'
    LEFT = 'left'
    KICKED = 'kicked'

    def __init__(self, user, status, **kwargs):
        # Required
        self.user = user
        self.status = status

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.ChatMember:
        """
        if not data:
            return None

        data = super(ChatMember, ChatMember).de_json(data, bot)

        data['user'] = User.de_json(data.get('user'), bot)

        return ChatMember(**data)
