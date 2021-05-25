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
"""This module contains an object that represents a Telegram LabeledPrice."""

from typing import Any

from telegram import TelegramObject


class LabeledPrice(TelegramObject):
    """This object represents a portion of the price for goods or services.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`label` and :attr:`amount` are equal.

    Args:
        label (:obj:`str`): Portion label.
        amount (:obj:`int`): Price of the product in the smallest units of the currency (integer,
            not float/double). For example, for a price of US$ 1.45 pass ``amount = 145``.
            See the :obj:`exp` parameter in
            `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_,
            it shows the number of digits past the decimal point for each currency
            (2 for the majority of currencies).
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        label (:obj:`str`): Portion label.
        amount (:obj:`int`): Price of the product in the smallest units of the currency.

    """

    def __init__(self, label: str, amount: int, **_kwargs: Any):
        self.label = label
        self.amount = amount

        self._id_attrs = (self.label, self.amount)
