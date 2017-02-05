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
"""This module contains an object that represents a Telegram ReplyKeyboardRemove."""
from telegram import ReplyMarkup
from telegram.utils.deprecate import warn_deprecate_obj


class ReplyKeyboardRemove(ReplyMarkup):
    """This object represents a Telegram ReplyKeyboardRemove.

    Attributes:
        remove_keyboard (bool): Always True.
        selective (bool):

    Args:
        selective (Optional[bool]): Use this parameter if you want to remove the keyboard for
            specific users only. Targets:
                1) users that are @mentioned in the text of the Message object;
                2) if the bot's message is a reply (has reply_to_message_id), sender of the
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
