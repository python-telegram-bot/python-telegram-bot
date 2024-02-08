#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""This module contains an object that represents a Telegram KeyboardButton."""

from typing import TYPE_CHECKING, Optional, Union

from telegram._keyboardbuttonpolltype import KeyboardButtonPollType
from telegram._keyboardbuttonrequest import (
    KeyboardButtonRequestChat,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestUsers,
)
from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict
from telegram._utils.warnings_transition import (
    warn_about_deprecated_arg_return_new_arg,
    warn_about_deprecated_attr_in_property,
)
from telegram._webappinfo import WebAppInfo

if TYPE_CHECKING:
    from telegram import Bot


class KeyboardButton(TelegramObject):
    """
    This object represents one button of the reply keyboard. For simple text buttons, :obj:`str`
    can be used instead of this object to specify text of the button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`text`, :attr:`request_contact`, :attr:`request_location`,
    :attr:`request_poll`, :attr:`web_app`, :attr:`request_users` and :attr:`request_chat` are
    equal.

    Note:
        * Optional fields are mutually exclusive.
        * :attr:`request_contact` and :attr:`request_location` options will only work in Telegram
          versions released after 9 April, 2016. Older clients will display unsupported message.
        * :attr:`request_poll` option will only work in Telegram versions released after 23
          January, 2020. Older clients will display unsupported message.
        * :attr:`web_app` option will only work in Telegram versions released after 16 April, 2022.
          Older clients will display unsupported message.
        * :attr:`request_users` and :attr:`request_chat` options will only work in Telegram
          versions released after 3 February, 2023. Older clients will display unsupported
          message.

    .. versionchanged:: 20.0
       :attr:`web_app` is considered as well when comparing objects of this type in terms of
       equality.
    .. versionchanged:: 20.5
       :attr:`request_users` and :attr:`request_chat` are considered as well when
       comparing objects of this type in terms of equality.

    Args:
        text (:obj:`str`): Text of the button. If none of the optional fields are used, it will be
            sent to the bot as a message when the button is pressed.
        request_contact (:obj:`bool`, optional): If :obj:`True`, the user's phone number will be
            sent as a contact when the button is pressed. Available in private chats only.
        request_location (:obj:`bool`, optional): If :obj:`True`, the user's current location will
            be sent when the button is pressed. Available in private chats only.
        request_poll (:class:`~telegram.KeyboardButtonPollType`, optional): If specified, the user
            will be asked to create a poll and send it to the bot when the button is pressed.
            Available in private chats only.
        web_app (:class:`~telegram.WebAppInfo`, optional): If specified, the described `Web App
            <https://core.telegram.org/bots/webapps>`_ will be launched when the button is pressed.
            The Web App will be able to send a :attr:`Message.web_app_data` service message.
            Available in private chats only.

            .. versionadded:: 20.0
        request_user (:class:`KeyboardButtonRequestUser` | :class:`KeyboardButtonRequestUsers`, \
            optional): Alias for
            :attr:`request_users`.

            .. versionadded:: 20.1
            .. deprecated:: 20.8
               Bot API 7.0 deprecates this argument in favor of ref`request_users`.

        request_users (:class:`KeyboardButtonRequestUsers`, optional): If specified, pressing the
            button will open a list of suitable users. Tapping on any user will send its
            identifier to the bot in a :attr:`telegram.Message.user_shared` service message.
            Available in private chats only.

            .. versionadded:: 20.8
        request_chat (:class:`KeyboardButtonRequestChat`, optional): If specified, pressing the
            button will open a list of suitable chats. Tapping on a chat will send its
            identifier to the bot in a :attr:`telegram.Message.chat_shared` service message.
            Available in private chats only.

            .. versionadded:: 20.1
    Attributes:
        text (:obj:`str`): Text of the button. If none of the optional fields are used, it will be
            sent to the bot as a message when the button is pressed.
        request_contact (:obj:`bool`): Optional. If :obj:`True`, the user's phone number will be
            sent as a contact when the button is pressed. Available in private chats only.
        request_location (:obj:`bool`): Optional. If :obj:`True`, the user's current location will
            be sent when the button is pressed. Available in private chats only.
        request_poll (:class:`~telegram.KeyboardButtonPollType`): Optional. If specified,
            the user will be asked to create a poll and send it to the bot when the button is
            pressed. Available in private chats only.
        web_app (:class:`~telegram.WebAppInfo`): Optional. If specified, the described `Web App
            <https://core.telegram.org/bots/webapps>`_ will be launched when the button is pressed.
            The Web App will be able to send a :attr:`Message.web_app_data` service message.
            Available in private chats only.

            .. versionadded:: 20.0
        request_users (:class:`KeyboardButtonRequestUsers`): Optional. If specified, pressing the
            button will open a list of suitable users. Tapping on any user will send its
            identifier to the bot in a :attr:`telegram.Message.user_shared` service message.
            Available in private chats only.

            .. versionadded:: 20.8
        request_chat (:class:`KeyboardButtonRequestChat`): Optional. If specified, pressing the
            button will open a list of suitable chats. Tapping on a chat will send its
            identifier to the bot in a :attr:`telegram.Message.chat_shared` service message.
            Available in private chats only.

            .. versionadded:: 20.1
    """

    __slots__ = (
        "request_chat",
        "request_contact",
        "request_location",
        "request_poll",
        "request_users",
        "text",
        "web_app",
    )

    def __init__(
        self,
        text: str,
        request_contact: Optional[bool] = None,
        request_location: Optional[bool] = None,
        request_poll: Optional[KeyboardButtonPollType] = None,
        web_app: Optional[WebAppInfo] = None,
        request_user: Optional[
            Union[KeyboardButtonRequestUsers, KeyboardButtonRequestUser]
        ] = None,
        request_chat: Optional[KeyboardButtonRequestChat] = None,
        request_users: Optional[KeyboardButtonRequestUsers] = None,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)

        # Required
        self.text: str = text
        # Optionals
        self.request_contact: Optional[bool] = request_contact
        self.request_location: Optional[bool] = request_location
        self.request_poll: Optional[KeyboardButtonPollType] = request_poll
        self.web_app: Optional[WebAppInfo] = web_app
        self.request_users: Optional[KeyboardButtonRequestUsers] = (
            warn_about_deprecated_arg_return_new_arg(
                deprecated_arg=request_user,
                new_arg=request_users,
                deprecated_arg_name="request_user",
                new_arg_name="request_users",
                bot_api_version="7.0",
            )
        )
        self.request_chat: Optional[KeyboardButtonRequestChat] = request_chat

        self._id_attrs = (
            self.text,
            self.request_contact,
            self.request_location,
            self.request_poll,
            self.web_app,
            self.request_users,
            self.request_chat,
        )

        self._freeze()

    @property
    def request_user(self) -> Optional[KeyboardButtonRequestUsers]:
        """Optional[:class:`KeyboardButtonRequestUsers`]: Alias for :attr:`request_users`.

        .. versionadded:: 20.1
        .. deprecated:: 20.8
           Bot API 7.0 deprecates this attribute in favor of :attr:`request_users`.
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="request_user",
            new_attr_name="request_users",
            bot_api_version="7.0",
        )
        return self.request_users

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: "Bot") -> Optional["KeyboardButton"]:
        """See :meth:`telegram.TelegramObject.de_json`."""
        data = cls._parse_data(data)

        if not data:
            return None

        data["request_poll"] = KeyboardButtonPollType.de_json(data.get("request_poll"), bot)
        data["request_users"] = KeyboardButtonRequestUsers.de_json(data.get("request_users"), bot)
        data["request_chat"] = KeyboardButtonRequestChat.de_json(data.get("request_chat"), bot)
        data["web_app"] = WebAppInfo.de_json(data.get("web_app"), bot)

        return super().de_json(data=data, bot=bot)
