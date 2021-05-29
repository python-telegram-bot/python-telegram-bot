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
"""This module contains an object that represents a Telegram OrderInfo."""

from typing import TYPE_CHECKING, Any, Optional

from telegram import ShippingAddress, TelegramObject
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class OrderInfo(TelegramObject):
    """This object represents information about an order.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`name`, :attr:`phone_number`, :attr:`email` and
    :attr:`shipping_address` are equal.

    Args:
        name (:obj:`str`, optional): User name.
        phone_number (:obj:`str`, optional): User's phone number.
        email (:obj:`str`, optional): User email.
        shipping_address (:class:`telegram.ShippingAddress`, optional): User shipping address.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        name (:obj:`str`): Optional. User name.
        phone_number (:obj:`str`): Optional. User's phone number.
        email (:obj:`str`): Optional. User email.
        shipping_address (:class:`telegram.ShippingAddress`): Optional. User shipping address.

    """

    __slots__ = ('email', 'shipping_address', 'phone_number', 'name', '_id_attrs')

    def __init__(
        self,
        name: str = None,
        phone_number: str = None,
        email: str = None,
        shipping_address: str = None,
        **_kwargs: Any,
    ):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.shipping_address = shipping_address

        self._id_attrs = (self.name, self.phone_number, self.email, self.shipping_address)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['OrderInfo']:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return cls()

        data['shipping_address'] = ShippingAddress.de_json(data.get('shipping_address'), bot)

        return cls(**data)
