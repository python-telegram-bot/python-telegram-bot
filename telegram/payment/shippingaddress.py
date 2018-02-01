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
"""This module contains an object that represents a Telegram ShippingAddress."""

from telegram import TelegramObject


class ShippingAddress(TelegramObject):
    """This object represents a Telegram ShippingAddress.

    Attributes:
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        state (:obj:`str`): State, if applicable.
        city (:obj:`str`): City.
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Second line for the address.
        post_code (:obj:`str`): Address post code.

    Args:
        country_code (:obj:`str`): ISO 3166-1 alpha-2 country code.
        state (:obj:`str`): State, if applicable.
        city (:obj:`str`): City.
        street_line1 (:obj:`str`): First line for the address.
        street_line2 (:obj:`str`): Second line for the address.
        post_code (:obj:`str`): Address post code.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, country_code, state, city, street_line1, street_line2, post_code, **kwargs):
        self.country_code = country_code
        self.state = state
        self.city = city
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.post_code = post_code

        self._id_attrs = (self.country_code, self.state, self.city, self.street_line1,
                          self.street_line2, self.post_code)

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
