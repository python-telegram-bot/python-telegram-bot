#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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
"""This module contains an object that represents a Telegram Invoice."""

from dataclasses import dataclass
from telegram import TelegramObject
from typing import Any


@dataclass(eq=False)
class Invoice(TelegramObject):
    """This object contains basic information about an invoice.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`title`, :attr:`description`, :attr:`start_parameter`,
    :attr:`currency` and :attr:`total_amount` are equal.

    Attributes:
        title (:obj:`str`): Product name.
        description (:obj:`str`): Product description.
        start_parameter (:obj:`str`): Unique bot deep-linking parameter.
        currency (:obj:`str`): Three-letter ISO 4217 currency code.
        total_amount (:obj:`int`): Total price in the smallest units of the currency.

    Args:
        title (:obj:`str`): Product name.
        description (:obj:`str`): Product description.
        start_parameter (:obj:`str`): Unique bot deep-linking parameter that can be used to
            generate this invoice.
        currency (:obj:`str`): Three-letter ISO 4217 currency code.
        total_amount (:obj:`int`): Total price in the smallest units of the currency (integer, not
            float/double). For example, for a price of US$ 1.45 pass amount = 145.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int

    def __post_init__(self, **kwargs: Any) -> None:
        self._id_attrs = (
            self.title,
            self.description,
            self.start_parameter,
            self.currency,
            self.total_amount,
        )
