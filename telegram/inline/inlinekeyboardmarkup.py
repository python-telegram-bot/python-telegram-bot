#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
"""This module contains an object that represents a Telegram InlineKeyboardMarkup."""

from telegram import ReplyMarkup, InlineKeyboardButton


class InlineKeyboardMarkup(ReplyMarkup):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.

    Attributes:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): Array of button rows,
            each represented by an Array of InlineKeyboardButton objects.

    Args:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): Array of button rows,
            each represented by an Array of InlineKeyboardButton objects.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, inline_keyboard, **kwargs):
        # Required
        self.inline_keyboard = inline_keyboard

    def to_dict(self):
        data = super(InlineKeyboardMarkup, self).to_dict()

        data['inline_keyboard'] = []
        for inline_keyboard in self.inline_keyboard:
            data['inline_keyboard'].append([x.to_dict() for x in inline_keyboard])

        return data

    @classmethod
    def de_json(cls, data, bot):
        if not data:
            return None
        keyboard = []
        for row in data['inline_keyboard']:
            tmp = []
            for col in row:
                tmp.append(InlineKeyboardButton.de_json(col, bot))
            keyboard.append(tmp)

        return cls(keyboard)

    @classmethod
    def from_button(cls, button, **kwargs):
        """Shortcut for::

            InlineKeyboardMarkup([[button]], **kwargs)

        Return an InlineKeyboardMarkup from a single InlineKeyboardButton

        Args:
            button (:class:`telegram.InlineKeyboardButton`): The button to use in the markup
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return cls([[button]], **kwargs)

    @classmethod
    def from_row(cls, button_row, **kwargs):
        """Shortcut for::

            InlineKeyboardMarkup([button_row], **kwargs)

        Return an InlineKeyboardMarkup from a single row of InlineKeyboardButtons

        Args:
            button_row (List[:class:`telegram.InlineKeyboardButton`]): The button to use in the
                markup
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return cls([button_row], **kwargs)

    @classmethod
    def from_column(cls, button_column, **kwargs):
        """Shortcut for::

            InlineKeyboardMarkup([[button] for button in button_column], **kwargs)

        Return an InlineKeyboardMarkup from a single column of InlineKeyboardButtons

        Args:
            button_column (List[:class:`telegram.InlineKeyboardButton`]): The button to use in the
                markup
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        button_grid = [[button] for button in button_column]
        return cls(button_grid, **kwargs)
