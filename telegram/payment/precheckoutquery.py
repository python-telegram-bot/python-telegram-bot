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
"""This module contains an object that represents a Telegram PreCheckoutQuery."""

from telegram import TelegramObject, User, OrderInfo


class PreCheckoutQuery(TelegramObject):
    """This object contains information about an incoming pre-checkout query.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        currency (:obj:`str`): Three-letter ISO 4217 currency code.
        total_amount (:obj:`int`): Total price in the smallest units of the currency.
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_option_id (:obj:`str`): Optional. Identifier of the shipping option chosen by the
            user.
        order_info (:class:`telegram.OrderInfo`): Optional. Order info provided by the user.
        bot (:class:`telegram.Bot`): Optional. The Bot to use for instance methods.

    Args:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        currency (:obj:`str`): Three-letter ISO 4217 currency code
        total_amount (:obj:`int`): Total price in the smallest units of the currency (integer, not
            float/double). For example, for a price of US$ 1.45 pass amount = 145. See the exp
            parameter in currencies.json, it shows the number of digits past the decimal point for
            each currency (2 for the majority of currencies).
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_option_id (:obj:`str`, optional): Identifier of the shipping option chosen by the
            user.
        order_info (:class:`telegram.OrderInfo`, optional): Order info provided by the user.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        data = super(PreCheckoutQuery, cls).de_json(data, bot)

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['order_info'] = OrderInfo.de_json(data.get('order_info'), bot)

        return cls(bot=bot, **data)

    def answer(self, *args, **kwargs):
        """Shortcut for::

            bot.answer_pre_checkout_query(update.pre_checkout_query.id, *args, **kwargs)

        Args:
            ok (:obj:`bool`): Specify True if everything is alright (goods are available, etc.) and
                the bot is ready to proceed with the order. Use False if there are any problems.
            error_message (:obj:`str`, optional): Required if ok is False. Error message in human
                readable form that explains the reason for failure to proceed with the checkout
                (e.g. "Sorry, somebody just bought the last of our amazing black T-shirts while you
                were busy filling out your payment details. Please choose a different color or
                garment!"). Telegram will display this message to the user.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return self.bot.answer_pre_checkout_query(self.id, *args, **kwargs)
