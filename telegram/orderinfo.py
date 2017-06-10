#!/usr/bin/env python
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
"""This module contains an object that represents a Telegram OrderInfo."""

from telegram import TelegramObject, ShippingAddress


class OrderInfo(TelegramObject):
    """This object represents information about an order.

    Attributes:
        name (Optional[str]): User name
        phone_number (Optional[str]): User's phone number
        email (Optional[str]): User email
        shipping_address (Optional[:class:`telegram.ShippingAddress`]): User shipping address
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, name=None, phone_number=None, email=None, shipping_address=None, **kwargs):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.shipping_address = shipping_address

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.OrderInfo:
        """
        if not data:
            return OrderInfo()

        data = super(OrderInfo, OrderInfo).de_json(data, bot)

        data['shipping_address'] = ShippingAddress.de_json(data.get('shipping_address'), bot)

        return OrderInfo(**data)
