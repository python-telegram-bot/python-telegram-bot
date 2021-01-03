#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains the classes that represent Telegram InputContactMessageContent."""

from typing import Any

from telegram import InputMessageContent


class InputContactMessageContent(InputMessageContent):
    """Represents the content of a contact message to be sent as the result of an inline query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`phone_number` is equal.

    Args:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`, optional): Contact's last name.
        vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
            0-2048 bytes.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`): Optional. Contact's last name.
        vcard (:obj:`str`): Optional. Additional data about the contact in the form of a vCard,
            0-2048 bytes.

    """

    def __init__(
        self,
        phone_number: str,
        first_name: str,
        last_name: str = None,
        vcard: str = None,
        **_kwargs: Any,
    ):
        # Required
        self.phone_number = phone_number
        self.first_name = first_name
        # Optionals
        self.last_name = last_name
        self.vcard = vcard

        self._id_attrs = (self.phone_number,)
