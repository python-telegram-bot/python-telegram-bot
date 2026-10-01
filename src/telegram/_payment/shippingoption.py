#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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

from typing import TYPE_CHECKING

from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field

if TYPE_CHECKING:
    from telegram import LabeledPrice


@tg_dataclass()
class ShippingOption(TelegramObject):
    """This object represents one shipping option.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`id` is equal.

    Examples:
        :any:`Payment Bot <examples.paymentbot>`

    Args:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (Sequence[:class:`telegram.LabeledPrice`]): List of price portions.

            .. versionchanged:: 20.0
                |sequenceclassargs|

    Attributes:
        id (:obj:`str`): Shipping option identifier.
        title (:obj:`str`): Option title.
        prices (tuple[:class:`telegram.LabeledPrice`]): List of price portions.

            .. versionchanged:: 20.0
                |tupleclassattrs|

    """

    id: str = tg_field(compare=True)
    title: str = tg_field()
    prices: tuple["LabeledPrice", ...] = tg_field(converter=parse_sequence_arg)
