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
"""This module contains objects that represent reply keyboards and buttons."""
from telegram import TelegramObject, ReplyMarkup
from telegram.utils.deprecate import warn_deprecate_obj


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


class ReplyKeyboardRemove(ReplyMarkup):
    """This object represents a Telegram ReplyKeyboardRemove.

    Attributes:
        remove_keyboard (bool): Always True.
        selective (bool):

    Args:
        selective (Optional[bool]): Use this parameter if you want to remove the keyboard for
            specific users only. Targets:

            - users that are @mentioned in the text of the Message object
            - if the bot's message is a reply (has reply_to_message_id), sender of the
              original message.

        **kwargs: Arbitrary keyword arguments.

    """

    def __init__(self, selective=False, **kwargs):
        # Required
        self.remove_keyboard = True
        # Optionals
        self.selective = bool(selective)

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot(telegram.Bot):

        Returns:
            telegram.ReplyKeyboardRemove

        """
        if not data:
            return None

        return ReplyKeyboardRemove(**data)


class ReplyKeyboardHide(object):
    def __new__(cls, hide_keyboard=True, selective=False, **kwargs):
        warn_deprecate_obj(ReplyKeyboardHide.__name__, ReplyKeyboardRemove.__name__)
        obj = ReplyKeyboardRemove.__new__(ReplyKeyboardRemove, selective)
        obj.__init__(selective)
        return obj


class KeyboardButton(TelegramObject):
    """
    This object represents one button of the reply keyboard. For simple
    text buttons String can be used instead of this object to specify text
    of the button.

    Args:
        text (str):
        request_location (Optional[bool]):
        request_contact (Optional[bool]):
    """

    def __init__(self, text, request_contact=None, request_location=None, **kwargs):
        # Required
        self.text = text
        # Optionals
        self.request_contact = request_contact
        self.request_location = request_location

    @staticmethod
    def de_json(data, bot):
        if not data:
            return None

        return KeyboardButton(**data)

    @staticmethod
    def de_list(data, bot):
        if not data:
            return []

        keyboards = list()
        for keyboard in data:
            keyboards.append(KeyboardButton.de_json(keyboard, bot))

        return keyboards
