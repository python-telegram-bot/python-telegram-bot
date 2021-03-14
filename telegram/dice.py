#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains an object that represents a Telegram Dice."""
from typing import Any, List, ClassVar

from telegram import TelegramObject, constants


class Dice(TelegramObject):
    """
    This object represents an animated emoji with a random value for currently supported base
    emoji. (The singular form of "dice" is "die". However, PTB mimics the Telegram API, which uses
    the term "dice".)

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`value` and :attr:`emoji` are equal.

    Note:
        If :attr:`emoji` is "🎯", a value of 6 currently represents a bullseye, while a value of 1
        indicates that the dartboard was missed. However, this behaviour is undocumented and might
        be changed by Telegram.

        If :attr:`emoji` is "🏀", a value of 4 or 5 currently score a basket, while a value of 1 to
        3 indicates that the basket was missed. However, this behaviour is undocumented and might
        be changed by Telegram.

        If :attr:`emoji` is "⚽", a value of 4 to 5 currently scores a goal, while a value of 1 to
        3 indicates that the goal was missed. However, this behaviour is undocumented and might
        be changed by Telegram.

        If :attr:`emoji` is "🎳", a value of 6 knocks all the pins, while a value of 1 means all
        the pins were missed. However, this behaviour is undocumented and might be changed by
        Telegram.

        If :attr:`emoji` is "🎰", each value corresponds to a unique combination of symbols, which
        can be found at our `wiki <https://git.io/JkeC6>`_. However, this behaviour is undocumented
        and might be changed by Telegram.

    Args:
        value (:obj:`int`): Value of the dice. 1-6 for dice, darts and bowling balls, 1-5 for
            basketball and football/soccer ball, 1-64 for slot machine.
        emoji (:obj:`str`): Emoji on which the dice throw animation is based.

    Attributes:
        value (:obj:`int`): Value of the dice.
        emoji (:obj:`str`): Emoji on which the dice throw animation is based.

    """

    def __init__(self, value: int, emoji: str, **_kwargs: Any):
        self.value = value
        self.emoji = emoji

        self._id_attrs = (self.value, self.emoji)

    DICE: ClassVar[str] = constants.DICE_DICE
    """:const:`telegram.constants.DICE_DICE`"""
    DARTS: ClassVar[str] = constants.DICE_DARTS
    """:const:`telegram.constants.DICE_DARTS`"""
    BASKETBALL: ClassVar[str] = constants.DICE_BASKETBALL
    """:const:`telegram.constants.DICE_BASKETBALL`"""
    FOOTBALL: ClassVar[str] = constants.DICE_FOOTBALL
    """:const:`telegram.constants.DICE_FOOTBALL`"""
    SLOT_MACHINE: ClassVar[str] = constants.DICE_SLOT_MACHINE
    """:const:`telegram.constants.DICE_SLOT_MACHINE`"""
    BOWLING: ClassVar[str] = constants.DICE_BOWLING
    """
    :const:`telegram.constants.DICE_BOWLING`

    .. versionadded:: 13.4
    """
    ALL_EMOJI: ClassVar[List[str]] = constants.DICE_ALL_EMOJI
    """:const:`telegram.constants.DICE_ALL_EMOJI`"""
