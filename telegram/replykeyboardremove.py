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
"""This module contains an object that represents a Telegram ReplyKeyboardRemove."""
from telegram import ReplyMarkup


class ReplyKeyboardRemove(ReplyMarkup):
    """
    Upon receiving a message with this object, Telegram clients will remove the current custom
    keyboard and display the default letter-keyboard. By default, custom keyboards are displayed
    until a new keyboard is sent by a bot. An exception is made for one-time keyboards that are
    hidden immediately after the user presses a button (see :class:`telegram.ReplyKeyboardMarkup`).

    Attributes:
        remove_keyboard (:obj:`True`): Requests clients to remove the custom keyboard.
        selective (:obj:`bool`): Optional. Use this parameter if you want to remove the keyboard
            for specific users only.

    Example:
        A user votes in a poll, bot returns confirmation message in reply to the vote and removes
        the keyboard for that user, while still showing the keyboard with poll options to users who
        haven't voted yet.

    Args:
        selective (:obj:`bool`, optional): Use this parameter if you want to remove the keyboard
            for specific users only. Targets:

            1) users that are @mentioned in the text of the Message object
            2) if the bot's message is a reply (has reply_to_message_id), sender of the original
               message.

        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    """

    def __init__(self, selective=False, **kwargs):
        # Required
        self.remove_keyboard = True
        # Optionals
        self.selective = bool(selective)
