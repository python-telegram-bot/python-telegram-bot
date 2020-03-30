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
    This object represents a dice with random value from 1 to 6. (Yes, Telegram is aware of the
    proper singular of die. They don't like it.)

    Attributes:
        value (:obj:`int`): Value of the dice, 1-6.

    Args:
        value (:obj:`int`): Value of the dice, 1-6.
    """
    def __init__(self, value, **kwargs):
        self.value = value
