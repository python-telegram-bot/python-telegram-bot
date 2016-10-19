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
"""This module contains an object that represents a Telegram User."""

from telegram import TelegramObject


class User(TelegramObject):
    """This object represents a Telegram User.

    Attributes:
        id (int):
        first_name (str):
        last_name (str):
        username (str):
        type (str):

    Args:
        id (int):
        first_name (str):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        type (Optional[str]):
        last_name (Optional[str]):
        username (Optional[str]):
        bot (Optional[Bot]): The Bot to use for instance methods
    """

    def __init__(self, id, first_name, type='', last_name='', username='', bot=None, **kwargs):
        # Required
        self.id = int(id)
        self.first_name = first_name
        # Optionals
        self.type = type
        self.last_name = last_name
        self.username = username

        self.bot = bot

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

        return User(bot=bot, **data)

    def get_profile_photos(self, *args, **kwargs):
        """
        Shortcut for ``bot.getUserProfilePhotos(update.message.from_user.id, *args, **kwargs)``
        """
        return self.bot.getUserProfilePhotos(self.id, *args, **kwargs)
