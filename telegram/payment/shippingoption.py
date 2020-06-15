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
"""This module contains an object that represents a Telegram ShippingOption."""

from telegram import TelegramObject


class ShippingOption(TelegramObject):
    """This object represents one shipping option.

    Attributes:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (List[:class:`telegram.LabeledPrice`]): List of price portions.

    Args:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (List[:class:`telegram.LabeledPrice`]): List of price portions.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, id, title, prices, **kwargs):
        self.id = id
        self.title = title
        self.prices = prices

        self._id_attrs = (self.id,)

    def to_dict(self):
        data = super().to_dict()

        data['prices'] = [p.to_dict() for p in self.prices]

        return data
