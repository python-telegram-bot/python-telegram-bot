#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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

from typing import TYPE_CHECKING, List

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import LabeledPrice  # noqa


class ShippingOption(TelegramObject):
    """This object represents one shipping option.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Examples:
        :any:`Payment Bot <examples.paymentbot>`

    Args:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (List[:class:`telegram.LabeledPrice`]): List of price portions.

    Attributes:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (List[:class:`telegram.LabeledPrice`]): List of price portions.

    """

    __slots__ = ("prices", "title", "id")

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        title: str,
        prices: List["LabeledPrice"],
        *,
        api_kwargs: JSONDict = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        self.id = id  # pylint: disable=invalid-name
        self.title = title
        self.prices = prices

        self._id_attrs = (self.id,)
