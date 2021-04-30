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
"""This module contains an object that represents a Telegram PreCheckoutQuery."""

from typing import TYPE_CHECKING, Any, Optional

from telegram import OrderInfo, TelegramObject, User
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import JSONDict, ODVInput

if TYPE_CHECKING:
    from telegram import Bot


class PreCheckoutQuery(TelegramObject):
    """This object contains information about an incoming pre-checkout query.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Note:
        In Python ``from`` is a reserved word, use ``from_user`` instead.

    Args:
        id (:obj:`str`): Unique query identifier.
        from_user (:class:`telegram.User`): User who sent the query.
        currency (:obj:`str`): Three-letter ISO 4217 currency code.
        total_amount (:obj:`int`): Total price in the smallest units of the currency (integer, not
            float/double). For example, for a price of US$ 1.45 pass ``amount = 145``.
            See the :obj:`exp` parameter in
            `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_,
            it shows the number of digits past the decimal point for each currency
            (2 for the majority of currencies).
        invoice_payload (:obj:`str`): Bot specified invoice payload.
        shipping_option_id (:obj:`str`, optional): Identifier of the shipping option chosen by the
            user.
        order_info (:class:`telegram.OrderInfo`, optional): Order info provided by the user.
        bot (:class:`telegram.Bot`, optional): The Bot to use for instance methods.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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

    """

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        from_user: User,
        currency: str,
        total_amount: int,
        invoice_payload: str,
        shipping_option_id: str = None,
        order_info: OrderInfo = None,
        bot: 'Bot' = None,
        **_kwargs: Any,
    ):
        self.id = id  # pylint: disable=C0103
        self.from_user = from_user
        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.shipping_option_id = shipping_option_id
        self.order_info = order_info

        self.bot = bot

        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['PreCheckoutQuery']:
        data = cls.parse_data(data)

        if not data:
            return None

        data['from_user'] = User.de_json(data.pop('from'), bot)
        data['order_info'] = OrderInfo.de_json(data.get('order_info'), bot)

        return cls(bot=bot, **data)

    def answer(  # pylint: disable=C0103
        self,
        ok: bool,
        error_message: str = None,
        timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: JSONDict = None,
    ) -> bool:
        """Shortcut for::

            bot.answer_pre_checkout_query(update.pre_checkout_query.id, *args, **kwargs)

        For the documentation of the arguments, please see
        :meth:`telegram.Bot.answer_pre_checkout_query`.

        """
        return self.bot.answer_pre_checkout_query(
            pre_checkout_query_id=self.id,
            ok=ok,
            error_message=error_message,
            timeout=timeout,
            api_kwargs=api_kwargs,
        )
