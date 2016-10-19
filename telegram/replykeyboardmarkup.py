#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains an object that represents a Telegram
ReplyKeyboardMarkup."""

from telegram import ReplyMarkup, KeyboardButton


class ReplyKeyboardMarkup(ReplyMarkup):
    """This object represents a Telegram ReplyKeyboardMarkup.

    Attributes:
        keyboard (List[List[:class:`telegram.KeyboardButton`]]):
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
                 resize_keyboard=False,
                 one_time_keyboard=False,
                 selective=False,
                 **kwargs):
        # Required
        self.keyboard = keyboard
        # Optionals
        self.resize_keyboard = bool(resize_keyboard)
        self.one_time_keyboard = bool(one_time_keyboard)
        self.selective = bool(selective)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.ReplyKeyboardMarkup:
        """
        if not data:
            return None

        data['keyboard'] = [KeyboardButton.de_list(keyboard, bot) for keyboard in data['keyboard']]

        return ReplyKeyboardMarkup(**data)

    def to_dict(self):
        data = super(ReplyKeyboardMarkup, self).to_dict()

        data['keyboard'] = []
        for row in self.keyboard:
            r = []
            for button in row:
                if hasattr(button, 'to_dict'):
                    r.append(button.to_dict())  # telegram.KeyboardButton
                else:
                    r.append(button)  # str
            data['keyboard'].append(r)
        return data
