#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
    """This object represents a custom keyboard with reply options.

    Attributes:
        keyboard ([[:class:`telegram.KeyboardButton`]]): Array of button rows,
                each represented by an Array of :class:`telegram.KeyboardButton` objects.
        resize_keyboard (bool): Optional. Requests clients to resize the keyboard
                vertically for optimal fit (e.g., make the keyboard smaller if there
                are just two rows of buttons). Defaults to false, in which case the custom
                keyboard is always of the same height as the app's standard keyboard.
        one_time_keyboard (bool): Optional. Requests clients to hide the keyboard as soon as it's
                been used. The keyboard will still be available, but clients will automatically
                display the usual letter-keyboard in the chat - the user can press a special
                button in the input field to see the custom keyboard again. Defaults to false.
        selective (bool): Optional. Use this parameter if you want to show the keyboard to
                specific users only. Targets: 1) users that are @mentioned in the text of the
                Message object; 2) if the bot's message is a reply (has reply_to_message_id),
                sender of the original message.

    Example:
        A user requests to change the bot's language, bot replies to the request with a keyboard
        to select the new language. Other users in the group don't see the keyboard.

    Args:
        keyboard (list(list([str | :class:`telegram.KeyboardButton` ]))): Array of button rows,
                each represented by an Array of :class:`telegram.KeyboardButton` objects.
        resize_keyboard (Optional[bool]): Requests clients to resize the keyboard vertically for
                optimal fit (e.g., make the keyboard smaller if there are just two rows of
                buttons). Defaults to false, in which case the custom keyboard is always of the
                same height as the app's standard keyboard.
        one_time_keyboard (Optional[bool]): Requests clients to hide the keyboard as soon as it's
                been used. The keyboard will still be available, but clients will automatically
                display the usual letter-keyboard in the chat - the user can press a special
                button in the input field to see the custom keyboard again. Defaults to false.
        selective (Optional[bool]): Use this parameter if you want to show the keyboard to
                specific users only. Targets: 1) users that are @mentioned in the text of the
                Message object; 2) if the bot's message is a reply (has reply_to_message_id),
                sender of the original message.
        **kwargs: Arbitrary keyword arguments.
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
            bot (:class:`telegram.Bot`):

        Returns:
            :class:`telegram.ReplyKeyboardMarkup`:
        """
        if not data:
            return None

        data = super(ReplyKeyboardMarkup, ReplyKeyboardMarkup).de_json(data, bot)

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
