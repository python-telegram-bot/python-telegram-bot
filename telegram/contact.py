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
"""This module contains an object that represents a Telegram Contact."""

from telegram import TelegramObject


class Contact(TelegramObject):
    """This object represents a Telegram Contact.

    Attributes:
        phone_number (str):
        first_name (str):
        last_name (str):
        user_id (int):

    Args:
        phone_number (str):
        first_name (str):
        last_name (Optional[str]):
        user_id (Optional[int]):
        **kwargs: Arbitrary keyword arguments.

    """

    def __init__(self, phone_number, first_name, last_name=None, user_id=None, **kwargs):
        # Required
        self.phone_number = str(phone_number)
        self.first_name = first_name
        # Optionals
        self.last_name = last_name
        self.user_id = user_id

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.Contact:
        """
        if not data:
            return None

        return Contact(**data)
