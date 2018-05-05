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
"""This module contains an object that represents a Telegram Invoice."""

from telegram import TelegramObject


class Invoice(TelegramObject):
    """This object contains basic information about an invoice.

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

    def __init__(self, title, description, start_parameter, currency, total_amount, **kwargs):
        self.title = title
        self.description = description
        self.start_parameter = start_parameter
        self.currency = currency
        self.total_amount = total_amount

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)
