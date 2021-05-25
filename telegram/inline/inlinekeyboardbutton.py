#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains an object that represents a Telegram InlineKeyboardButton."""

from typing import TYPE_CHECKING, Any

from telegram import TelegramObject

if TYPE_CHECKING:
    from telegram import CallbackGame, LoginUrl


class InlineKeyboardButton(TelegramObject):
    """This object represents one button of an inline keyboard.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text`, :attr:`url`, :attr:`login_url`, :attr:`callback_data`,
    :attr:`switch_inline_query`, :attr:`switch_inline_query_current_chat`, :attr:`callback_game`
    and :attr:`pay` are equal.

    Note:
        You must use exactly one of the optional fields. Mind that :attr:`callback_game` is not
        working as expected. Putting a game short name in it might, but is not guaranteed to work.

    Args:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`): HTTP or tg:// url to be opened when button is pressed.
        login_url (:class:`telegram.LoginUrl`, optional): An HTTP URL used to automatically
            authorize the user. Can be used as a replacement for the Telegram Login Widget.
        callback_data (:obj:`str`, optional): Data to be sent in a callback query to the bot when
            button is pressed, UTF-8 1-64 bytes.
        switch_inline_query (:obj:`str`, optional): If set, pressing the button will prompt the
            user to select one of their chats, open that chat and insert the bot's username and the
            specified inline query in the input field. Can be empty, in which case just the bot's
            username will be inserted. This offers an easy way for users to start using your bot
            in inline mode when they are currently in a private chat with it. Especially useful
            when combined with switch_pm* actions - in this case the user will be automatically
            returned to the chat they switched from, skipping the chat selection screen.
        switch_inline_query_current_chat (:obj:`str`, optional): If set, pressing the button will
            insert the bot's username and the specified inline query in the current chat's input
            field. Can be empty, in which case only the bot's username will be inserted. This
            offers a quick way for the user to open your bot in inline mode in the same chat - good
            for selecting something from multiple options.
        callback_game (:class:`telegram.CallbackGame`, optional): Description of the game that will
            be launched when the user presses the button. This type of button must always be
            the ``first`` button in the first row.
        pay (:obj:`bool`, optional): Specify :obj:`True`, to send a Pay button. This type of button
            must always be the ``first`` button in the first row.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`): Optional. HTTP or tg:// url to be opened when button is pressed.
        login_url (:class:`telegram.LoginUrl`): Optional. An HTTP URL used to automatically
            authorize the user. Can be used as a replacement for the Telegram Login Widget.
        callback_data (:obj:`str`): Optional. Data to be sent in a callback query to the bot when
            button is pressed, UTF-8 1-64 bytes.
        switch_inline_query (:obj:`str`): Optional. Will prompt the user to select one of their
            chats, open that chat and insert the bot's username and the specified inline query in
            the input field. Can be empty, in which case just the bot’s username will be inserted.
        switch_inline_query_current_chat (:obj:`str`): Optional. Will insert the bot's username and
            the specified inline query in the current chat's input field. Can be empty, in which
            case just the bot’s username will be inserted.
        callback_game (:class:`telegram.CallbackGame`): Optional. Description of the game that will
            be launched when the user presses the button.
        pay (:obj:`bool`): Optional. Specify :obj:`True`, to send a Pay button.

    """

    def __init__(
        self,
        text: str,
        url: str = None,
        callback_data: str = None,
        switch_inline_query: str = None,
        switch_inline_query_current_chat: str = None,
        callback_game: 'CallbackGame' = None,
        pay: bool = None,
        login_url: 'LoginUrl' = None,
        **_kwargs: Any,
    ):
        # Required
        self.text = text

        # Optionals
        self.url = url
        self.login_url = login_url
        self.callback_data = callback_data
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game
        self.pay = pay

        self._id_attrs = (
            self.text,
            self.url,
            self.login_url,
            self.callback_data,
            self.switch_inline_query,
            self.switch_inline_query_current_chat,
            self.callback_game,
            self.pay,
        )
