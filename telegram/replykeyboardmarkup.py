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
"""This module contains an object that represents a Telegram ReplyKeyboardMarkup."""

from telegram import ReplyMarkup, KeyboardButton
from telegram.utils.types import JSONDict
from typing import List, Union, Any


class ReplyKeyboardMarkup(ReplyMarkup):
    """This object represents a custom keyboard with reply options.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their the size of :attr:`keyboard` and all the buttons are equal.

    Attributes:
        keyboard (List[List[:class:`telegram.KeyboardButton` | :obj:`str`]]): Array of button rows.
        resize_keyboard (:obj:`bool`): Optional. Requests clients to resize the keyboard.
        one_time_keyboard (:obj:`bool`): Optional. Requests clients to hide the keyboard as soon as
            it's been used.
        selective (:obj:`bool`): Optional. Show the keyboard to specific users only.

    Example:
        A user requests to change the bot's language, bot replies to the request with a keyboard
        to select the new language. Other users in the group don't see the keyboard.

    Args:
        keyboard (List[List[:obj:`str` | :class:`telegram.KeyboardButton`]]): Array of button rows,
                each represented by an Array of :class:`telegram.KeyboardButton` objects.
        resize_keyboard (:obj:`bool`, optional): Requests clients to resize the keyboard vertically
            for optimal fit (e.g., make the keyboard smaller if there are just two rows of
            buttons). Defaults to :obj:`False`, in which case the custom keyboard is always of the
            same height as the app's standard keyboard.
        one_time_keyboard (:obj:`bool`, optional): Requests clients to hide the keyboard as soon as
            it's been used. The keyboard will still be available, but clients will automatically
            display the usual letter-keyboard in the chat - the user can press a special button in
            the input field to see the custom keyboard again. Defaults to :obj:`False`.
        selective (:obj:`bool`, optional): Use this parameter if you want to show the keyboard to
            specific users only. Targets:

            1) Users that are @mentioned in the text of the Message object.
            2) If the bot's message is a reply (has ``reply_to_message_id``), sender of the
               original message.

            Defaults to :obj:`False`.

        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(
        self,
        keyboard: List[List[Union[str, KeyboardButton]]] = None,
        resize_keyboard: bool = False,
        one_time_keyboard: bool = False,
        selective: bool = False,
        **kwargs: Any,
    ):
        # Required
        k = []
        if keyboard is not None:
            for row in keyboard:
                r = []
                for button in row:
                    if isinstance(button, KeyboardButton):
                        r.append(button)  # telegram.KeyboardButton
                    else:
                        r.append(KeyboardButton(button))  # str
                k.append(r)
        self.keyboard = [[]] if len(k) == 0 else k

        # Optionals
        self.resize_keyboard = bool(resize_keyboard)
        self.one_time_keyboard = bool(one_time_keyboard)
        self.selective = bool(selective)

    def to_dict(self) -> JSONDict:
        data = super().to_dict()

        data['keyboard'] = []
        for row in self.keyboard:
            r: List[Union[JSONDict, str]] = []
            for button in row:
                if isinstance(button, KeyboardButton):
                    r.append(button.to_dict())  # telegram.KeyboardButton
                else:
                    r.append(button)  # str
            data['keyboard'].append(r)
        return data

    @classmethod
    def from_button(
        cls,
        button: Union[KeyboardButton, str],
        resize_keyboard: bool = False,
        one_time_keyboard: bool = False,
        selective: bool = False,
        **kwargs: Any,
    ) -> 'ReplyKeyboardMarkup':
        """Shortcut for::

            ReplyKeyboardMarkup([[button]], **kwargs)

        Return a ReplyKeyboardMarkup from a single KeyboardButton.

        Args:
            button (:class:`telegram.KeyboardButton` | :obj:`str`): The button to use in
                the markup.
            resize_keyboard (:obj:`bool`, optional): Requests clients to resize the keyboard
                vertically for optimal fit (e.g., make the keyboard smaller if there are just two
                rows of buttons). Defaults to :obj:`False`, in which case the custom keyboard is
                always of the same height as the app's standard keyboard.
            one_time_keyboard (:obj:`bool`, optional): Requests clients to hide the keyboard as
                soon as it's been used. The keyboard will still be available, but clients will
                automatically display the usual letter-keyboard in the chat - the user can press
                a special button in the input field to see the custom keyboard again.
                Defaults to :obj:`False`.
            selective (:obj:`bool`, optional): Use this parameter if you want to show the keyboard
                to specific users only. Targets:

                1) Users that are @mentioned in the text of the Message object.
                2) If the bot's message is a reply (has reply_to_message_id), sender of the
                    original message.

                Defaults to :obj:`False`.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.
        """
        return cls(
            [[button]],
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            **kwargs,
        )

    @classmethod
    def from_row(
        cls,
        button_row: List[Union[str, KeyboardButton]],
        resize_keyboard: bool = False,
        one_time_keyboard: bool = False,
        selective: bool = False,
        **kwargs: Any,
    ) -> 'ReplyKeyboardMarkup':
        """Shortcut for::

            ReplyKeyboardMarkup([button_row], **kwargs)

        Return a ReplyKeyboardMarkup from a single row of KeyboardButtons.

        Args:
            button_row (List[:class:`telegram.KeyboardButton` | :obj:`str`]): The button to use in
                the markup.
            resize_keyboard (:obj:`bool`, optional): Requests clients to resize the keyboard
                vertically for optimal fit (e.g., make the keyboard smaller if there are just two
                rows of buttons). Defaults to :obj:`False`, in which case the custom keyboard is
                always of the same height as the app's standard keyboard.
            one_time_keyboard (:obj:`bool`, optional): Requests clients to hide the keyboard as
                soon as it's been used. The keyboard will still be available, but clients will
                automatically display the usual letter-keyboard in the chat - the user can press
                a special button in the input field to see the custom keyboard again.
                Defaults to :obj:`False`.
            selective (:obj:`bool`, optional): Use this parameter if you want to show the keyboard
                to specific users only. Targets:

                1) Users that are @mentioned in the text of the Message object.
                2) If the bot's message is a reply (has reply_to_message_id), sender of the
                    original message.

                Defaults to :obj:`False`.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        return cls(
            [button_row],
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            **kwargs,
        )

    @classmethod
    def from_column(
        cls,
        button_column: List[Union[str, KeyboardButton]],
        resize_keyboard: bool = False,
        one_time_keyboard: bool = False,
        selective: bool = False,
        **kwargs: Any,
    ) -> 'ReplyKeyboardMarkup':
        """Shortcut for::

            ReplyKeyboardMarkup([[button] for button in button_column], **kwargs)

        Return a ReplyKeyboardMarkup from a single column of KeyboardButtons.

        Args:
            button_column (List[:class:`telegram.KeyboardButton` | :obj:`str`]): The button to use
                in the markup.
            resize_keyboard (:obj:`bool`, optional): Requests clients to resize the keyboard
                vertically for optimal fit (e.g., make the keyboard smaller if there are just two
                rows of buttons). Defaults to :obj:`False`, in which case the custom keyboard is
                always of the same height as the app's standard keyboard.
            one_time_keyboard (:obj:`bool`, optional): Requests clients to hide the keyboard as
                soon as it's been used. The keyboard will still be available, but clients will
                automatically display the usual letter-keyboard in the chat - the user can press
                a special button in the input field to see the custom keyboard again.
                Defaults to :obj:`False`.
            selective (:obj:`bool`, optional): Use this parameter if you want to show the keyboard
                to specific users only. Targets:

                1) Users that are @mentioned in the text of the Message object.
                2) If the bot's message is a reply (has reply_to_message_id), sender of the
                    original message.

                Defaults to :obj:`False`.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        """
        button_grid = [[button] for button in button_column]
        return cls(
            button_grid,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            **kwargs,
        )

    def add_button(
            self,
            button: Union[KeyboardButton, str],
            from_row: int = None,
            column: int = None,
            **kwargs: Any,
    ) -> 'ReplyKeyboardMarkup':
        """Convenient method to add :class:`telegram.KeyboardButton` to the specified
        row and column.

        Args:
            button (:class:`telegram.KeyboardButton` | :obj:`str`): The button to be added to
                the markup
            from_row (:obj:`int`, optional): Set index to specify the row to add the button.
                The value should be included in the row indexes. Leave `None` to set the last row
                as default.
            column (:obj:`int`, optional): Set index for the button insert location of the row.
                Leave `None`, to append the button to the row by default.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.ReplyKeyboardMarkup`

        Raises:
            :class:`IndexError`

        """
        button = button if isinstance(button, KeyboardButton) else KeyboardButton(button)
        row = len(self.keyboard) - 1 if from_row is None else from_row
        if row >= len(self.keyboard) or row < -len(self.keyboard):
            raise IndexError('row index out of range')
        if column is None:
            self.keyboard[row].append(button)
        else:
            if column >= len(self.keyboard[row]):
                self.keyboard[row].append(button)
            elif column < -len(self.keyboard[row]):
                self.keyboard[row].insert(0, button)
            else:
                self.keyboard[row].insert(column, button)
        return self

    def add_row(
            self,
            button_row: List[Union[str, KeyboardButton]] = None,
            index: int = None,
            **kwargs: Any
    ) -> 'ReplyKeyboardMarkup':
        """Convenient method to add List[:class:`telegram.KeyboardButton` | :obj:`str`] into
        a specified location.

        Args:
            button_row: (List[:class:`telegram.KeyboardButton` | :obj:`str`]): The button to
                add to the markup
            index (:obj:`int`, optional): Set index for the row insert location of the markup.
                Leave `None`, to append the row to the end of markup.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.ReplyKeyboardMarkup`
        """
        row = []
        if button_row is not None:
            for button in button_row:
                if isinstance(button, KeyboardButton):
                    row.append(button)
                else:
                    row.append(KeyboardButton(button))

        if index is None:
            self.keyboard.append(row)
        else:
            if index >= len(self.keyboard):
                self.keyboard.append(row)
            elif index < -len(self.keyboard):
                self.keyboard.insert(0, row)
            else:
                self.keyboard.insert(index, row)
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            if len(self.keyboard) != len(other.keyboard):
                return False
            for idx, row in enumerate(self.keyboard):
                if len(row) != len(other.keyboard[idx]):
                    return False
                for jdx, button in enumerate(row):
                    if button != other.keyboard[idx][jdx]:
                        return False
            return True
        return super(ReplyKeyboardMarkup, self).__eq__(other)  # pylint: disable=no-member

    def __hash__(self) -> int:
        return hash(
            (
                tuple(tuple(button for button in row) for row in self.keyboard),
                self.resize_keyboard,
                self.one_time_keyboard,
                self.selective,
            )
        )
