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
"""This module contains an object that represents a Telegram ShippingAddress."""

from telegram._telegramobject import TelegramObject
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class ShippingAddress(TelegramObject):
    """This object represents a Telegram ShippingAddress.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their  :attr:`country_code`, :attr:`state`, :attr:`city`,
    :attr:`street_line1`, :attr:`street_line2` and :attr:`post_code` are equal.

    Args:
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        state (:obj:`str`): State, if applicable.
        city (:obj:`str`): City.
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Second line for the address.
        post_code (:obj:`str`): Address post code.

    Attributes:
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        state (:obj:`str`): State, if applicable.
        city (:obj:`str`): City.
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Second line for the address.
        post_code (:obj:`str`): Address post code.

    """

    country_code: str = tg_field(compare=True)
    state: str = tg_field(compare=True)
    city: str = tg_field(compare=True)
    street_line1: str = tg_field(compare=True)
    street_line2: str = tg_field(compare=True)
    post_code: str = tg_field(compare=True)
