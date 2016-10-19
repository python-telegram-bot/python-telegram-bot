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
"""
This module contains an object that represents a Telegram ChosenInlineResult
"""

from telegram import TelegramObject, User, Location


class ChosenInlineResult(TelegramObject):
    """This object represents a Telegram ChosenInlineResult.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        result_id (str):
        from_user (:class:`telegram.User`):
        query (str):
        location (:class:`telegram.Location`):
        inline_message_id (str):

    Args:
        result_id (str):
        from_user (:class:`telegram.User`):
        query (str):
        location (Optional[:class:`telegram.Location`]):
        inline_message_id (Optional[str]):
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 result_id,
                 from_user,
                 query,
                 location=None,
                 inline_message_id=None,
                 **kwargs):
        # Required
        self.result_id = result_id
        self.from_user = from_user
        self.query = query
        # Optionals
        self.location = location
        self.inline_message_id = inline_message_id

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.ChosenInlineResult:
        """
        if not data:
            return None

# Required
        data['from_user'] = User.de_json(data.pop('from'), bot)
        # Optionals
        data['location'] = Location.de_json(data.get('location'), bot)

        return ChosenInlineResult(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(ChosenInlineResult, self).to_dict()

        # Required
        data['from'] = data.pop('from_user', None)

        return data
