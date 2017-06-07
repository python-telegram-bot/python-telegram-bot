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
"""This module contains an object that represents a Telegram ShippingOption."""

from telegram import TelegramObject, LabeledPrice


class ShippingOption(TelegramObject):
    """This object represents one shipping option.

    Note:
        * In Python `from` is a reserved word, use `from_user` instead.

    Attributes:
        id (str): Shipping option identifier
        title (str): Option title
        prices (List[:class:`telegram.LabeledPrice`]): List of price portions
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self, id, title, prices, **kwargs):
        self.id = id
        self.title = title
        self.prices = prices

        self._id_attrs = (self.id,)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.ShippingOption:
        """
        if not data:
            return None

        data = super(ShippingOption, ShippingOption).de_json(data, bot)

        data['prices'] = LabeledPrice.de_list(data.get('prices'), bot)

        return ShippingOption(**data)

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = super(ShippingOption, self).to_dict()

        data['prices'] = [p.to_dict() for p in self.prices]

        return data
