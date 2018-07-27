#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
    """This object represents a phone contact.

    Attributes:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`): Optional. Contact's last name.
        user_id (:obj:`int`): Optional. Contact's user identifier in Telegram.

    Args:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`, optional): Contact's last name.
        user_id (:obj:`int`, optional): Contact's user identifier in Telegram.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, phone_number, first_name, last_name=None, user_id=None, **kwargs):
        # Required
        self.phone_number = str(phone_number)
        self.first_name = first_name
        # Optionals
        self.last_name = last_name
        self.user_id = user_id

        self._id_attrs = (self.phone_number,)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
