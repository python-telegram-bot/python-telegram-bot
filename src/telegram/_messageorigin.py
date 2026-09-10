#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
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
"""This module contains the classes that represent Telegram MessageOigin."""

import datetime as dtm
from typing import ClassVar

from telegram import constants
from telegram._chat import Chat
from telegram._telegramobject import TelegramObject
from telegram._user import User
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class MessageOrigin(TelegramObject):
    """
    Base class for telegram MessageOrigin object, it can be one of:

    * :class:`MessageOriginUser`
    * :class:`MessageOriginHiddenUser`
    * :class:`MessageOriginChat`
    * :class:`MessageOriginChannel`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` and :attr:`date` are equal.

    .. versionadded:: 20.8

    Args:
        type (:obj:`str`): Type of the message origin, can be on of:
            :attr:`~telegram.MessageOrigin.USER`, :attr:`~telegram.MessageOrigin.HIDDEN_USER`,
            :attr:`~telegram.MessageOrigin.CHAT`, or :attr:`~telegram.MessageOrigin.CHANNEL`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|

    Attributes:
        type (:obj:`str`): Type of the message origin, can be on of:
            :attr:`~telegram.MessageOrigin.USER`, :attr:`~telegram.MessageOrigin.HIDDEN_USER`,
            :attr:`~telegram.MessageOrigin.CHAT`, or :attr:`~telegram.MessageOrigin.CHANNEL`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "user": "MessageOriginUser",
            "hidden_user": "MessageOriginHiddenUser",
            "chat": "MessageOriginChat",
            "channel": "MessageOriginChannel",
        },
    )

    USER: ClassVar[str] = constants.MessageOriginType.USER
    """:const:`telegram.constants.MessageOriginType.USER`"""
    HIDDEN_USER: ClassVar[str] = constants.MessageOriginType.HIDDEN_USER
    """:const:`telegram.constants.MessageOriginType.HIDDEN_USER`"""
    CHAT: ClassVar[str] = constants.MessageOriginType.CHAT
    """:const:`telegram.constants.MessageOriginType.CHAT`"""
    CHANNEL: ClassVar[str] = constants.MessageOriginType.CHANNEL
    """:const:`telegram.constants.MessageOriginType.CHANNEL`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.MessageOriginType, value, value)

    # Required by all subclasses
    type: str = tg_field(compare=True, converter=_type_converter)
    date: dtm.datetime = tg_field(compare=True)


@tg_dataclass()
class MessageOriginUser(MessageOrigin):
    """
    The message was originally sent by a known user.

    .. versionadded:: 20.8

    Args:
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_user (:class:`telegram.User`): User that sent the message originally.

    Attributes:
        type (:obj:`str`): Type of the message origin. Always
            :tg-const:`~telegram.MessageOrigin.USER`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_user (:class:`telegram.User`): User that sent the message originally.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=MessageOrigin.USER)

    sender_user: User = tg_field()


@tg_dataclass()
class MessageOriginHiddenUser(MessageOrigin):
    """
    The message was originally sent by an unknown user.

    .. versionadded:: 20.8

    Args:
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_user_name (:obj:`str`): Name of the user that sent the message originally.

    Attributes:
        type (:obj:`str`): Type of the message origin. Always
            :tg-const:`~telegram.MessageOrigin.HIDDEN_USER`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_user_name (:obj:`str`): Name of the user that sent the message originally.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=MessageOrigin.HIDDEN_USER)

    sender_user_name: str = tg_field()


@tg_dataclass()
class MessageOriginChat(MessageOrigin):
    """
    The message was originally sent on behalf of a chat to a group chat.

    .. versionadded:: 20.8

    Args:
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_chat (:class:`telegram.Chat`): Chat that sent the message originally.
        author_signature (:obj:`str`, optional): For messages originally sent by an anonymous chat
            administrator, original message author signature

    Attributes:
        type (:obj:`str`): Type of the message origin. Always
            :tg-const:`~telegram.MessageOrigin.CHAT`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        sender_chat (:class:`telegram.Chat`): Chat that sent the message originally.
        author_signature (:obj:`str`): Optional. For messages originally sent by an anonymous chat
            administrator, original message author signature
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=MessageOrigin.CHAT)

    sender_chat: Chat = tg_field()
    author_signature: str | None = tg_field(default=None)


@tg_dataclass()
class MessageOriginChannel(MessageOrigin):
    """
    The message was originally sent to a channel chat.

    .. versionadded:: 20.8

    Args:
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        chat (:class:`telegram.Chat`): Channel chat to which the message was originally sent.
        message_id (:obj:`int`): Unique message identifier inside the chat.
        author_signature (:obj:`str`, optional): Signature of the original post author.

    Attributes:
        type (:obj:`str`): Type of the message origin. Always
            :tg-const:`~telegram.MessageOrigin.CHANNEL`.
        date (:obj:`datetime.datetime`): Date the message was sent originally.
            |datetime_localization|
        chat (:class:`telegram.Chat`): Channel chat to which the message was originally sent.
        message_id (:obj:`int`): Unique message identifier inside the chat.
        author_signature (:obj:`str`): Optional. Signature of the original post author.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=MessageOrigin.CHANNEL)

    chat: Chat = tg_field()
    message_id: int = tg_field()
    author_signature: str | None = tg_field(default=None)
