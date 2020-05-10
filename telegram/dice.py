#!/usr/bin/env python
# pylint: disable=R0903
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
"""This module contains an object that represents a Telegram Dice."""
from telegram import TelegramObject


class Dice(TelegramObject):
    """
    This object represents a dice with random value from 1 to 6 for currently supported base eomji.
    (The singular form of "dice" is "die". However, PTB mimics the Telegram API, which uses the
    term "dice".)

    Note:
        If :attr:`emoji` is "🎯", a value of 6 currently represents a bullseye, while a value of 1
        indicates that the dartboard was missed. However, this behaviour is undocumented and might
        be changed by Telegram.

    Attributes:
        value (:obj:`int`): Value of the dice.
        emoji (:obj:`str`): Emoji on which the dice throw animation is based.

    Args:
        value (:obj:`int`): Value of the dice, 1-6.
        emoji (:obj:`str`): Emoji on which the dice throw animation is based.
    """
    def __init__(self, value, emoji, **kwargs):
        self.value = value
        self.emoji = emoji

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None

        return cls(**data)

    DICE = '🎲'
    """:obj:`str`: '🎲'"""
    DARTS = '🎯'
    """:obj:`str`: '🎯'"""
    ALL_EMOJI = [DICE, DARTS]
    """List[:obj:`str`]: List of all supported base emoji. Currently :attr:`DICE` and
    :attr:`DARTS`."""
