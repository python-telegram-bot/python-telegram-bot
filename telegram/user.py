#!/usr/bin/env python
# pylint: disable=C0103,W0622
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
"""This module contains an object that represents a Telegram User."""

from telegram import TelegramObject


class User(TelegramObject):
    """This object represents a Telegram User.

    Attributes:
        id (int): Unique identifier for this user or bot
        first_name (str): User's or bot's first name
        last_name (str): User's or bot's last name
        username (str): User's or bot's username
        language_code (str): IETF language tag of the user's language
        type (str): Deprecated

    Args:
        id (int): Unique identifier for this user or bot
        first_name (str): User's or bot's first name
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        type (Optional[str]): Deprecated
        last_name (Optional[str]): User's or bot's last name
        username (Optional[str]): User's or bot's username
        language_code (Optional[str]): IETF language tag of the user's language
        bot (Optional[telegram.Bot]): The Bot to use for instance methods
    """

    def __init__(self,
                 id,
                 first_name,
                 type=None,
                 last_name=None,
                 username=None,
                 language_code=None,
                 bot=None,
                 **kwargs):
        # Required
        self.id = int(id)
        self.first_name = first_name
        # Optionals
        self.type = type
        self.last_name = last_name
        self.username = username
        self.language_code = language_code

        self.bot = bot

        self._id_attrs = (self.id,)

    @property
    def name(self):
        """str: """
        if self.username:
            return '@%s' % self.username
        if self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        return self.first_name

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.User:
        """
        if not data:
            return None

        data = super(User, User).de_json(data, bot)

        return User(bot=bot, **data)

    def get_profile_photos(self, *args, **kwargs):
        """
        Shortcut for ``bot.get_user_profile_photos(update.message.from_user.id, *args, **kwargs)``
        """
        return self.bot.get_user_profile_photos(self.id, *args, **kwargs)

    @staticmethod
    def de_list(data, bot):
        """
        Args:
            data (list):
            bot (telegram.Bot):

        Returns:
            List<telegram.User>:
        """
        if not data:
            return []

        users = list()
        for user in data:
            users.append(User.de_json(user, bot))

        return users
