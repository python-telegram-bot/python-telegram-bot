#!/usr/bin/env python
# pylint: disable=R0902,R0912,R0913
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <devs@python-telegram-bot.org>
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
"""This module contains an object that represents a Telegram InlineQuery"""

from telegram import TelegramObject, User, Location


class InlineQuery(TelegramObject):
    """This object represents a Telegram InlineQuery.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (str):
        from_user (:class:`telegram.User`):
        query (str):
        offset (str):

    Args:
        id (int):
        from_user (:class:`telegram.User`):
        query (str):
        offset (str):
        location (optional[:class:`telegram.Location`]):
        bot (Optional[Bot]): The Bot to use for instance methods
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, id, from_user, query, offset, location=None, bot=None, **kwargs):
        # Required
        self.id = id
        self.from_user = from_user
        self.query = query
        self.offset = offset

        # Optional
        self.location = location

        self.bot = bot

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.InlineQuery:
        """
        data = super(InlineQuery, InlineQuery).de_json(data, bot)

        if not data:
            return None

        data['from_user'] = User.de_json(data.get('from'), bot)
        data['location'] = Location.de_json(data.get('location'), bot)

        return InlineQuery(bot=bot, **data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(InlineQuery, self).to_dict()

        # Required
        data['from'] = data.pop('from_user', None)

        return data

    def answer(self, *args, **kwargs):
        """Shortcut for ``bot.answerInlineQuery(update.inline_query.id, *args, **kwargs)``"""
        return self.bot.answerInlineQuery(self.id, *args, **kwargs)
