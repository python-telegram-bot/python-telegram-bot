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
"""This module contains an object that represents a Telegram InlineKeyboardButton."""

from typing import TYPE_CHECKING, Any, Optional, Union

from telegram._games.callbackgame import CallbackGame
from telegram._loginurl import LoginUrl
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict
from telegram._webappinfo import WebAppInfo

if TYPE_CHECKING:
    from telegram import Bot


class InlineKeyboardButton(TelegramObject):
    """This object represents one button of an inline keyboard.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text`, :attr:`url`, :attr:`login_url`, :attr:`callback_data`,
    :attr:`switch_inline_query`, :attr:`switch_inline_query_current_chat`, :attr:`callback_game`,
    :attr:`web_app` and :attr:`pay` are equal.

    Note:
        * You must use exactly one of the optional fields. Mind that :attr:`callback_game` is not
          working as expected. Putting a game short name in it might, but is not guaranteed to
          work.
        * If your bot allows for arbitrary callback data, in keyboards returned in a response
          from telegram, :attr:`callback_data` maybe be an instance of
          :class:`telegram.ext.InvalidCallbackData`. This will be the case, if the data
          associated with the button was already deleted.

          .. versionadded:: 13.6

        * Since Bot API 5.5, it's now allowed to mention users by their ID in inline keyboards.
          This will only work in Telegram versions released after December 7, 2021.
          Older clients will display *unsupported message*.

    Warning:
        * If your bot allows your arbitrary callback data, buttons whose callback data is a
          non-hashable object will become unhashable. Trying to evaluate ``hash(button)`` will
          result in a :class:`TypeError`.

          .. versionchanged:: 13.6

        * After Bot API 6.1, only ``HTTPS`` links will be allowed in :paramref:`login_url`.

    .. seealso:: `Inline Keyboard Example 1 <examples.inlinekeyboard.html>`_,
        `Inline Keyboard Example 2 <examples.inlinekeyboard2.html>`_,
        :class:`telegram.InlineKeyboardMarkup`

    .. versionchanged:: 20.0
       :attr:`web_app` is considered as well when comparing objects of this type in terms of
       equality.

    Args:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`, optional): HTTP or tg:// url to be opened when the button is pressed.
            Links ``tg://user?id=<user_id>`` can be used to mention a user by
            their ID without using a username, if this is allowed by their privacy settings.

            .. versionchanged:: 13.9
               You can now mention a user using ``tg://user?id=<user_id>``.
        login_url (:class:`telegram.LoginUrl`, optional): An ``HTTPS`` URL used to automatically
            authorize the user. Can be used as a replacement for the Telegram Login Widget.

            Caution:
                Only ``HTTPS`` links are allowed after Bot API 6.1.
        callback_data (:obj:`str` | :obj:`object`, optional): Data to be sent in a callback query
            to the bot when button is pressed, UTF-8 1-64 bytes. If the bot instance allows
            arbitrary callback data, anything can be passed.

            Tip:
                The value entered here will be available in :attr:`telegram.CallbackQuery.data`.

        web_app (:obj:`telegram.WebAppInfo`, optional): Description of the `Web App
            <https://core.telegram.org/bots/webapps>`_  that will be launched when the user presses
            the button. The Web App will be able to send an arbitrary message on behalf of the user
            using the method :meth:`~telegram.Bot.answer_web_app_query`. Available only in
            private chats between a user and the bot.

            .. versionadded:: 20.0
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
            must always be the `first` button in the first row and can only be used in invoice
            messages.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        text (:obj:`str`): Label text on the button.
        url (:obj:`str`): Optional. HTTP or tg:// url to be opened when the button is pressed.
            Links ``tg://user?id=<user_id>`` can be used to mention a user by
            their ID without using a username, if this is allowed by their privacy settings.

            .. versionchanged:: 13.9
               You can now mention a user using ``tg://user?id=<user_id>``.
        login_url (:class:`telegram.LoginUrl`): Optional. An ``HTTPS`` URL used to automatically
            authorize the user. Can be used as a replacement for the Telegram Login Widget.

            Caution:
                Only ``HTTPS`` links are allowed after Bot API 6.1.
        callback_data (:obj:`str` | :obj:`object`): Optional. Data to be sent in a callback query
            to the bot when button is pressed, UTF-8 1-64 bytes.
        web_app (:obj:`telegram.WebAppInfo`): Optional. Description of the `Web App
            <https://core.telegram.org/bots/webapps>`_  that will be launched when the user presses
            the button. The Web App will be able to send an arbitrary message on behalf of the user
            using the method :meth:`~telegram.Bot.answer_web_app_query`. Available only in
            private chats between a user and the bot.

            .. versionadded:: 20.0
        switch_inline_query (:obj:`str`): Optional. Will prompt the user to select one of their
            chats, open that chat and insert the bot's username and the specified inline query in
            the input field. Can be empty, in which case just the bot's username will be inserted.
        switch_inline_query_current_chat (:obj:`str`): Optional. Will insert the bot's username and
            the specified inline query in the current chat's input field. Can be empty, in which
            case just the bot's username will be inserted.
        callback_game (:class:`telegram.CallbackGame`): Optional. Description of the game that will
            be launched when the user presses the button.
        pay (:obj:`bool`): Optional. Specify :obj:`True`, to send a Pay button.

    """

    __slots__ = (
        "callback_game",
        "url",
        "switch_inline_query_current_chat",
        "callback_data",
        "pay",
        "switch_inline_query",
        "text",
        "login_url",
        "web_app",
    )

    def __init__(
        self,
        text: str,
        url: str = None,
        callback_data: Union[str, object] = None,
        switch_inline_query: str = None,
        switch_inline_query_current_chat: str = None,
        callback_game: CallbackGame = None,
        pay: bool = None,
        login_url: LoginUrl = None,
        web_app: WebAppInfo = None,
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
        self.web_app = web_app
        self._id_attrs = ()
        self._set_id_attrs()

    def _set_id_attrs(self) -> None:
        self._id_attrs = (
            self.text,
            self.url,
            self.login_url,
            self.callback_data,
            self.web_app,
            self.switch_inline_query,
            self.switch_inline_query_current_chat,
            self.callback_game,
            self.pay,
        )

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["InlineKeyboardButton"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["login_url"] = LoginUrl.de_json(data.get("login_url"), bot)
        data["web_app"] = WebAppInfo.de_json(data.get("web_app"), bot)
        data["callback_game"] = CallbackGame.de_json(data.get("callback_game"), bot)

        return cls(**data)

    def update_callback_data(self, callback_data: Union[str, object]) -> None:
        """
        Sets :attr:`callback_data` to the passed object. Intended to be used by
        :class:`telegram.ext.CallbackDataCache`.

        .. versionadded:: 13.6

        Args:
            callback_data (:class:`object`): The new callback data.
        """
        self.callback_data = callback_data
        self._set_id_attrs()
