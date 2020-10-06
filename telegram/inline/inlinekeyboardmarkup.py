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
"""This module contains an object that represents a Telegram InlineKeyboardMarkup."""

from telegram import ReplyMarkup, InlineKeyboardButton
from telegram.utils.types import JSONDict
from typing import Any, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from telegram import Bot


class InlineKeyboardMarkup(ReplyMarkup):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their the size of :attr:`inline_keyboard` and all the buttons are equal.

    Attributes:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): List of button rows,
            each represented by a list of InlineKeyboardButton objects.

    Args:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): List of button rows,
            each represented by a list of InlineKeyboardButton objects.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, inline_keyboard: List[List[InlineKeyboardButton]], **kwargs: Any):
        # Required
        self.inline_keyboard = inline_keyboard

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['inline_keyboard'] = []
        for inline_keyboard in self.inline_keyboard:
            data['inline_keyboard'].append([x.to_dict() for x in inline_keyboard])

        return data

    @classmethod
    def de_json(cls, data: Optional[JSONDict],
                bot: 'Bot') -> Optional['InlineKeyboardMarkup']:
        data = cls.parse_data(data)

        if not data:
            return None

        keyboard = []
        for row in data['inline_keyboard']:
            tmp = []
            for col in row:
                btn = InlineKeyboardButton.de_json(col, bot)
                if btn:
                    tmp.append(btn)
            keyboard.append(tmp)

        return cls(keyboard)

    @classmethod
    def from_button(cls, button: InlineKeyboardButton, **kwargs: Any) -> 'InlineKeyboardMarkup':
        """Shortcut for::

            InlineKeyboardMarkup([[button]], **kwargs)

        Return an InlineKeyboardMarkup from a single InlineKeyboardButton

        Args:
            button (:class:`telegram.InlineKeyboardButton`): The button to use in the markup
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return cls([[button]], **kwargs)

    @classmethod
    def from_row(cls, button_row: List[InlineKeyboardButton],
                 **kwargs: Any) -> 'InlineKeyboardMarkup':
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
    def from_column(cls, button_column: List[InlineKeyboardButton],
                    **kwargs: Any) -> 'InlineKeyboardMarkup':
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            if len(self.inline_keyboard) != len(other.inline_keyboard):
                return False
            for idx, row in enumerate(self.inline_keyboard):
                if len(row) != len(other.inline_keyboard[idx]):
                    return False
                for jdx, button in enumerate(row):
                    if button != other.inline_keyboard[idx][jdx]:
                        return False
            return True
        return super(InlineKeyboardMarkup, self).__eq__(other)  # pylint: disable=no-member

    def __hash__(self) -> int:
        return hash(tuple(tuple(button for button in row) for row in self.inline_keyboard))
