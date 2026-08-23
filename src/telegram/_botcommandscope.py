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
"""This module contains objects representing Telegram bot command scopes."""

from typing import ClassVar

from telegram import constants
from telegram._telegramobject import TelegramObject
from telegram._utils import enum
from telegram._utils.dataclass import tg_dataclass, tg_field


@tg_dataclass()
class BotCommandScope(TelegramObject):
    """Base class for objects that represent the scope to which bot commands are applied.
    Currently, the following 7 scopes are supported:

    * :class:`telegram.BotCommandScopeDefault`
    * :class:`telegram.BotCommandScopeAllPrivateChats`
    * :class:`telegram.BotCommandScopeAllGroupChats`
    * :class:`telegram.BotCommandScopeAllChatAdministrators`
    * :class:`telegram.BotCommandScopeChat`
    * :class:`telegram.BotCommandScopeChatAdministrators`
    * :class:`telegram.BotCommandScopeChatMember`

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` is equal. For subclasses with additional attributes,
    the notion of equality is overridden.

    Note:
        Please see the `official docs`_ on how Telegram determines which commands to display.

    .. _`official docs`: https://core.telegram.org/bots/api#determining-list-of-commands

    .. versionadded:: 13.7

    Args:
        type (:obj:`str`): Scope type.

    Attributes:
        type (:obj:`str`): Scope type.
    """

    __DE_JSON_DISPATCH__: ClassVar[tuple[str, dict[str, str]] | None] = (
        "type",
        {
            "default": "BotCommandScopeDefault",
            "all_private_chats": "BotCommandScopeAllPrivateChats",
            "all_group_chats": "BotCommandScopeAllGroupChats",
            "all_chat_administrators": "BotCommandScopeAllChatAdministrators",
            "chat": "BotCommandScopeChat",
            "chat_administrators": "BotCommandScopeChatAdministrators",
            "chat_member": "BotCommandScopeChatMember",
        },
    )

    # TODO: https://docs.python.org/3.13/library/typing.html#typing.ClassVar
    DEFAULT: ClassVar[str] = constants.BotCommandScopeType.DEFAULT
    """:const:`telegram.constants.BotCommandScopeType.DEFAULT`"""
    ALL_PRIVATE_CHATS: ClassVar[str] = constants.BotCommandScopeType.ALL_PRIVATE_CHATS
    """:const:`telegram.constants.BotCommandScopeType.ALL_PRIVATE_CHATS`"""
    ALL_GROUP_CHATS: ClassVar[str] = constants.BotCommandScopeType.ALL_GROUP_CHATS
    """:const:`telegram.constants.BotCommandScopeType.ALL_GROUP_CHATS`"""
    ALL_CHAT_ADMINISTRATORS: ClassVar[str] = constants.BotCommandScopeType.ALL_CHAT_ADMINISTRATORS
    """:const:`telegram.constants.BotCommandScopeType.ALL_CHAT_ADMINISTRATORS`"""
    CHAT: ClassVar[str] = constants.BotCommandScopeType.CHAT
    """:const:`telegram.constants.BotCommandScopeType.CHAT`"""
    CHAT_ADMINISTRATORS: ClassVar[str] = constants.BotCommandScopeType.CHAT_ADMINISTRATORS
    """:const:`telegram.constants.BotCommandScopeType.CHAT_ADMINISTRATORS`"""
    CHAT_MEMBER: ClassVar[str] = constants.BotCommandScopeType.CHAT_MEMBER
    """:const:`telegram.constants.BotCommandScopeType.CHAT_MEMBER`"""

    @staticmethod
    def _type_converter(value: str) -> str:
        return enum.get_member(constants.BotCommandScopeType, value, value)

    @staticmethod
    def _chat_id_converter(value: str | int) -> str | int:
        return value if isinstance(value, str) and value.startswith("@") else int(value)

    type: str = tg_field(compare=True, converter=_type_converter)


@tg_dataclass()
class BotCommandScopeDefault(BotCommandScope):
    """Represents the default scope of bot commands. Default commands are used if no commands with
    a `narrower scope`_ are specified for the user.

    .. _`narrower scope`: https://core.telegram.org/bots/api#determining-list-of-commands

    .. versionadded:: 13.7
    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.DEFAULT`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BotCommandScope.DEFAULT)


@tg_dataclass()
class BotCommandScopeAllPrivateChats(BotCommandScope):
    """Represents the scope of bot commands, covering all private chats.

    .. versionadded:: 13.7

    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.ALL_PRIVATE_CHATS`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BotCommandScope.ALL_PRIVATE_CHATS)


@tg_dataclass()
class BotCommandScopeAllGroupChats(BotCommandScope):
    """Represents the scope of bot commands, covering all group and supergroup chats.

    .. versionadded:: 13.7
    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.ALL_GROUP_CHATS`.
    """

    type: str = tg_field(init=False, default=BotCommandScope.ALL_GROUP_CHATS)


@tg_dataclass()
class BotCommandScopeAllChatAdministrators(BotCommandScope):
    """Represents the scope of bot commands, covering all group and supergroup chat administrators.

    .. versionadded:: 13.7
    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.ALL_CHAT_ADMINISTRATORS`.
    """

    # Attribute only (init=False)
    type: str = tg_field(init=False, default=BotCommandScope.ALL_CHAT_ADMINISTRATORS)


@tg_dataclass()
class BotCommandScopeChat(BotCommandScope):
    """Represents the scope of bot commands, covering a specific chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` and :attr:`chat_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|

    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.CHAT`.
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=BotCommandScope.CHAT)

    chat_id: str | int = tg_field(compare=True, converter=BotCommandScope._chat_id_converter)


@tg_dataclass()
class BotCommandScopeChatAdministrators(BotCommandScope):
    """Represents the scope of bot commands, covering all administrators of a specific group or
    supergroup chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` and :attr:`chat_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|
    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.CHAT_ADMINISTRATORS`.
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=BotCommandScope.CHAT_ADMINISTRATORS)

    chat_id: str | int = tg_field(compare=True, converter=BotCommandScope._chat_id_converter)


@tg_dataclass()
class BotCommandScopeChatMember(BotCommandScope):
    """Represents the scope of bot commands, covering a specific member of a group or supergroup
    chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`chat_id` and :attr:`user_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|
        user_id (:obj:`int`): Unique identifier of the target user.

    Attributes:
        type (:obj:`str`): Scope type :tg-const:`telegram.BotCommandScope.CHAT_MEMBER`.
        chat_id (:obj:`str` | :obj:`int`): |chat_id_group|
        user_id (:obj:`int`): Unique identifier of the target user.
    """

    # Attribute only (init=False)
    type: str = tg_field(compare=True, init=False, default=BotCommandScope.CHAT_MEMBER)

    chat_id: str | int = tg_field(compare=True, converter=BotCommandScope._chat_id_converter)
    user_id: int = tg_field(compare=True)
