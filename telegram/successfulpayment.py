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
"""This module contains an object that represents a Telegram SuccessfulPayment."""

from telegram import TelegramObject, OrderInfo


class SuccessfulPayment(TelegramObject):
    """This object contains basic information about a successful payment.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        currency (str): Three-letter ISO 4217 currency code
        total_amount (int): Total price in the smallest units of the currency (integer)
        invoice_payload (str): Bot specified invoice payload
        telegram_payment_charge_id (str): Telegram payment identifier
        provider_payment_charge_id (str): Provider payment identifier
        shipping_option_id (Optional[str]): Identifier of the shipping option chosen by the user
        order_info (Optional[:class:`telegram.OrderInfo`]): Order info provided by the user
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 currency,
                 total_amount,
                 invoice_payload,
                 telegram_payment_charge_id,
                 provider_payment_charge_id,
                 shipping_option_id=None,
                 order_info=None,
                 **kwargs):
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.order_info = order_info
        self.telegram_payment_charge_id = telegram_payment_charge_id
        self.provider_payment_charge_id = provider_payment_charge_id

        self._id_attrs = (self.telegram_payment_charge_id, self.provider_payment_charge_id)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.SuccessfulPayment:
        """
        if not data:
            return None

        data = super(SuccessfulPayment, SuccessfulPayment).de_json(data, bot)
        data['order_info'] = OrderInfo.de_json(data.get('order_info'), bot)

        return SuccessfulPayment(**data)
