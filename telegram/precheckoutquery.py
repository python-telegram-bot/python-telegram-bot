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
"""This module contains an object that represents a Telegram PreCheckoutQuery."""

from telegram import TelegramObject, User, OrderInfo


class PreCheckoutQuery(TelegramObject):
    """This object contains information about an incoming pre-checkout query.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (str): Unique query identifier
        from_user (:class:`telegram.User`): User who sent the query
        currency (str): Three-letter ISO 4217 currency code
        total_amount (int): Total price in the smallest units of the currency (integer)
        invoice_payload (str): Bot specified invoice payload
        shipping_option_id (Optional[str]): Identifier of the shipping option chosen by the user
        order_info (Optional[:class:`telegram.OrderInfo`]): Order info provided by the user
        bot (Optional[Bot]): The Bot to use for instance methods
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 id,
                 from_user,
                 currency,
                 total_amount,
                 invoice_payload,
                 shipping_option_id=None,
                 order_info=None,
                 bot=None,
                 **kwargs):
        self.id = id
        self.from_user = from_user
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.order_info = order_info

        self.bot = bot

        self._id_attrs = (self.id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.PreCheckoutQuery:
        """
        if not data:
            return None

        data = super(PreCheckoutQuery, PreCheckoutQuery).de_json(data, bot)

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['order_info'] = OrderInfo.de_json(data.get('order_info'), bot)

        return PreCheckoutQuery(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(PreCheckoutQuery, self).to_dict()

        data['from'] = data.pop('from_user', None)

        return data

    def answer(self, *args, **kwargs):
        """
        Shortcut for
        ``bot.answer_pre_checkout_query(update.pre_checkout_query.id, *args, **kwargs)``
        """
        return self.bot.answer_pre_checkout_query(self.id, *args, **kwargs)
