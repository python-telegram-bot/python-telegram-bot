#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class Contact(TelegramObject):
    """This object represents a phone contact.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`phone_number` is equal.

    Args:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`, optional): Contact's last name.
        user_id (:obj:`int`, optional): Contact's user identifier in Telegram.
        vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard.

    Attributes:
        phone_number (:obj:`str`): Contact's phone number.
        first_name (:obj:`str`): Contact's first name.
        last_name (:obj:`str`): Optional. Contact's last name.
        user_id (:obj:`int`): Optional. Contact's user identifier in Telegram.
        vcard (:obj:`str`): Optional. Additional data about the contact in the form of a vCard.

    """

    # Required
    phone_number: str = tg_field(compare=True)
    first_name: str = tg_field()
    # Optional
    last_name: str | None = tg_field(default=None)
    user_id: int | None = tg_field(default=None)
    vcard: str | None = tg_field(default=None)
