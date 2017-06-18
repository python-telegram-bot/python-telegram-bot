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
"""This module contains an object that represents a Telegram ShippingQuery."""

from telegram import TelegramObject, User, ShippingAddress


class ShippingQuery(TelegramObject):
    """This object contains information about an incoming shipping query.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (str): Unique query identifier
        from_user (:class:`telegram.User`): User who sent the query
        invoice_payload (str): Bot specified invoice payload
        shipping_address (:class:`telegram.ShippingQuery`): User specified shipping address
        bot (Optional[Bot]): The Bot to use for instance methods
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, id, from_user, invoice_payload, shipping_address, bot=None, **kwargs):
        self.id = id
        self.from_user = from_user
        self.invoice_payload = invoice_payload
        self.shipping_address = shipping_address

        self.bot = bot

        self._id_attrs = (self.id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.ShippingQuery:
        """
        if not data:
            return None

        data = super(ShippingQuery, ShippingQuery).de_json(data, bot)

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['shipping_address'] = ShippingAddress.de_json(data.get('shipping_address'), bot)

        return ShippingQuery(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(ShippingQuery, self).to_dict()

        data['from'] = data.pop('from_user', None)

        return data

    def answer(self, *args, **kwargs):
        """Shortcut for ``bot.answer_shipping_query(update.shipping_query.id, *args, **kwargs)``"""
        return self.bot.answer_shipping_query(self.id, *args, **kwargs)
