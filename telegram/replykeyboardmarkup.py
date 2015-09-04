#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

"""This module contains a object that represents a Telegram
ReplyKeyboardMarkup"""

from telegram import ReplyMarkup


class ReplyKeyboardMarkup(ReplyMarkup):
    """This object represents a Telegram ReplyKeyboardMarkup.

    Attributes:
        keyboard (List[List[str]]):
        resize_keyboard (bool):
        one_time_keyboard (bool):
        selective (bool):

    Args:
        keyboard (List[List[str]]):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        resize_keyboard (Optional[bool]):
        one_time_keyboard (Optional[bool]):
        selective (Optional[bool]):
    """

    def __init__(self,
                 keyboard,
                 **kwargs):
        # Required
        self.keyboard = keyboard
        # Optionals
        self.resize_keyboard = bool(kwargs.get('resize_keyboard', False))
        self.one_time_keyboard = bool(kwargs.get('one_time_keyboard', False))
        self.selective = bool(kwargs.get('selective', False))

    @staticmethod
    def de_json(data):
        """
        Args:
            data (str):

        Returns:
            telegram.ReplyKeyboardMarkup:
        """
        if not data:
            return None

        return ReplyKeyboardMarkup(**data)
