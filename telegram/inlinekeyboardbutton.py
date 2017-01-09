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
InlineKeyboardButton"""

from telegram import TelegramObject


class InlineKeyboardButton(TelegramObject):
    """This object represents a Telegram InlineKeyboardButton.

    Attributes:
        text (str):
        url (str):
        callback_data (str):
        switch_inline_query (str):
        switch_inline_query_current_chat (str):
        callback_game (:class:`telegram.CallbackGame`):

    Args:
        text (str): Label text on the button.
        url (Optional[str]): HTTP url to be opened when button is pressed.
        callback_data (Optional[str]):  Data to be sent in a callback query to the bot when button
            is pressed, 1-64 bytes.
        switch_inline_query (Optional[str]): If set, pressing the button will prompt the user to
            select one of their chats, open that chat and insert the bot's username and the
            specified inline query in the input field. Can be empty, in which case just the bot's
            username will be inserted.
        switch_inline_query_current_chat (Optional[str]): If set, pressing the button will insert
            the bot's username and the specified inline query in the current chat's input field.
            Can be empty, in which case only the bot's username will be inserted.
        callback_game (Optional[:class:`telegram.CallbackGame`]): Description of the game that will
            be launched when the user presses the button.
        **kwargs (dict): Arbitrary keyword arguments.

    """

    def __init__(self,
                 text,
                 url=None,
                 callback_data=None,
                 switch_inline_query=None,
                 switch_inline_query_current_chat=None,
                 callback_game=None,
                 **kwargs):
        # Required
        self.text = text

        # Optionals
        self.url = url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game

    @staticmethod
    def de_json(data, bot):
        """
        Args:
            data (dict):
            bot (telegram.Bot):

        Returns:
            telegram.InlineKeyboardButton:
        """
        data = super(InlineKeyboardButton, InlineKeyboardButton).de_json(data, bot)

        if not data:
            return None

        return InlineKeyboardButton(**data)

    @staticmethod
    def de_list(data, bot):
        if not data:
            return []

        inline_keyboards = list()
        for inline_keyboard in data:
            inline_keyboards.append(InlineKeyboardButton.de_json(inline_keyboard, bot))

        return inline_keyboards
