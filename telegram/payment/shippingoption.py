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
from telegram.utils.types import JSONDict
from typing import List, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import LabeledPrice  # noqa


class ShippingOption(TelegramObject):
    """This object represents one shipping option.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

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

    def __init__(self, id: str, title: str, prices: List['LabeledPrice'], **kwargs: Any):
        self.id = id
        self.title = title
        self.prices = prices

        self._id_attrs = (self.id,)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['prices'] = [p.to_dict() for p in self.prices]

        return data
