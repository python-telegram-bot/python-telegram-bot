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
"""This module contains an object that represents a Telegram InlineKeyboardMarkup."""

from typing import TYPE_CHECKING, Any, List, Optional

from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._telegramobject import TelegramObject
from telegram._utils.markup import check_keyboard_type
from telegram._utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


class InlineKeyboardMarkup(TelegramObject):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their size of :attr:`inline_keyboard` and all the buttons are equal.

    .. seealso:: `Inline Keyboard Example 1 <examples.inlinekeyboard.html>`_,
        `Inline Keyboard Example 2 <examples.inlinekeyboard2.html>`_

    Args:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): List of button rows,
            each represented by a list of InlineKeyboardButton objects.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        inline_keyboard (List[List[:class:`telegram.InlineKeyboardButton`]]): List of button rows,
            each represented by a list of InlineKeyboardButton objects.

    """

    __slots__ = ("inline_keyboard",)

    def __init__(self, inline_keyboard: List[List[InlineKeyboardButton]], **_kwargs: Any):
        if not check_keyboard_type(inline_keyboard):
            raise ValueError(
                "The parameter `inline_keyboard` should be a list of "
                "list of InlineKeyboardButtons"
            )
        # Required
        self.inline_keyboard = inline_keyboard

        self._id_attrs = (self.inline_keyboard,)

    def to_dict(self) -> JSONDict:
        """See :meth:`telegram.TelegramObject.to_dict`."""
        data = super().to_dict()

        data["inline_keyboard"] = []
        for inline_keyboard in self.inline_keyboard:
            data["inline_keyboard"].append([x.to_dict() for x in inline_keyboard])

        return data

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["InlineKeyboardMarkup"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        keyboard = []
        for row in data["inline_keyboard"]:
            tmp = []
            for col in row:
                btn = InlineKeyboardButton.de_json(col, bot)
                if btn:
                    tmp.append(btn)
            keyboard.append(tmp)

        return cls(keyboard)

    @classmethod
    def from_button(cls, button: InlineKeyboardButton, **kwargs: object) -> "InlineKeyboardMarkup":
        """Shortcut for::

            InlineKeyboardMarkup([[button]], **kwargs)

        Return an InlineKeyboardMarkup from a single InlineKeyboardButton

        Args:
            button (:class:`telegram.InlineKeyboardButton`): The button to use in the markup
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return cls([[button]], **kwargs)

    @classmethod
    def from_row(
        cls, button_row: List[InlineKeyboardButton], **kwargs: object
    ) -> "InlineKeyboardMarkup":
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
    def from_column(
        cls, button_column: List[InlineKeyboardButton], **kwargs: object
    ) -> "InlineKeyboardMarkup":
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

    def __hash__(self) -> int:
        return hash(tuple(tuple(button for button in row) for row in self.inline_keyboard))
