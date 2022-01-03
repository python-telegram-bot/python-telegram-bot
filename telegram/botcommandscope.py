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
# pylint: disable=W0622
"""This module contains objects representing Telegram bot command scopes."""
from typing import Any, Union, Optional, TYPE_CHECKING, Dict, Type

from telegram import TelegramObject, constants
from telegram.utils.types import JSONDict

if TYPE_CHECKING:
    from telegram import Bot


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

    __slots__ = ('type', '_id_attrs')

    DEFAULT = constants.BOT_COMMAND_SCOPE_DEFAULT
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_DEFAULT`"""
    ALL_PRIVATE_CHATS = constants.BOT_COMMAND_SCOPE_ALL_PRIVATE_CHATS
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_ALL_PRIVATE_CHATS`"""
    ALL_GROUP_CHATS = constants.BOT_COMMAND_SCOPE_ALL_GROUP_CHATS
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_ALL_GROUP_CHATS`"""
    ALL_CHAT_ADMINISTRATORS = constants.BOT_COMMAND_SCOPE_ALL_CHAT_ADMINISTRATORS
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_ALL_CHAT_ADMINISTRATORS`"""
    CHAT = constants.BOT_COMMAND_SCOPE_CHAT
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_CHAT`"""
    CHAT_ADMINISTRATORS = constants.BOT_COMMAND_SCOPE_CHAT_ADMINISTRATORS
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_CHAT_ADMINISTRATORS`"""
    CHAT_MEMBER = constants.BOT_COMMAND_SCOPE_CHAT_MEMBER
    """:const:`telegram.constants.BOT_COMMAND_SCOPE_CHAT_MEMBER`"""

    def __init__(self, type: str, **_kwargs: Any):
        self.type = type
        self._id_attrs = (self.type,)

    @classmethod
    def de_json(cls, data: Optional[JSONDict], bot: 'Bot') -> Optional['BotCommandScope']:
        """Converts JSON data to the appropriate :class:`BotCommandScope` object, i.e. takes
        care of selecting the correct subclass.

        Args:
            data (Dict[:obj:`str`, ...]): The JSON data.
            bot (:class:`telegram.Bot`): The bot associated with this object.

        Returns:
            The Telegram object.

        """
        data = cls._parse_data(data)

        if not data:
            return None

        _class_mapping: Dict[str, Type['BotCommandScope']] = {
            cls.DEFAULT: BotCommandScopeDefault,
            cls.ALL_PRIVATE_CHATS: BotCommandScopeAllPrivateChats,
            cls.ALL_GROUP_CHATS: BotCommandScopeAllGroupChats,
            cls.ALL_CHAT_ADMINISTRATORS: BotCommandScopeAllChatAdministrators,
            cls.CHAT: BotCommandScopeChat,
            cls.CHAT_ADMINISTRATORS: BotCommandScopeChatAdministrators,
            cls.CHAT_MEMBER: BotCommandScopeChatMember,
        }

        if cls is BotCommandScope:
            return _class_mapping.get(data['type'], cls)(**data, bot=bot)
        return cls(**data)


class BotCommandScopeDefault(BotCommandScope):
    """Represents the default scope of bot commands. Default commands are used if no commands with
    a `narrower scope`_ are specified for the user.

    .. _`narrower scope`: https://core.telegram.org/bots/api#determining-list-of-commands

    .. versionadded:: 13.7

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.DEFAULT`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=BotCommandScope.DEFAULT)


class BotCommandScopeAllPrivateChats(BotCommandScope):
    """Represents the scope of bot commands, covering all private chats.

    .. versionadded:: 13.7

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.ALL_PRIVATE_CHATS`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=BotCommandScope.ALL_PRIVATE_CHATS)


class BotCommandScopeAllGroupChats(BotCommandScope):
    """Represents the scope of bot commands, covering all group and supergroup chats.

    .. versionadded:: 13.7

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.ALL_GROUP_CHATS`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=BotCommandScope.ALL_GROUP_CHATS)


class BotCommandScopeAllChatAdministrators(BotCommandScope):
    """Represents the scope of bot commands, covering all group and supergroup chat administrators.

    .. versionadded:: 13.7

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.ALL_CHAT_ADMINISTRATORS`.
    """

    __slots__ = ()

    def __init__(self, **_kwargs: Any):
        super().__init__(type=BotCommandScope.ALL_CHAT_ADMINISTRATORS)


class BotCommandScopeChat(BotCommandScope):
    """Represents the scope of bot commands, covering a specific chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` and :attr:`chat_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.CHAT`.
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)
    """

    __slots__ = ('chat_id',)

    def __init__(self, chat_id: Union[str, int], **_kwargs: Any):
        super().__init__(type=BotCommandScope.CHAT)
        self.chat_id = (
            chat_id if isinstance(chat_id, str) and chat_id.startswith('@') else int(chat_id)
        )
        self._id_attrs = (self.type, self.chat_id)


class BotCommandScopeChatAdministrators(BotCommandScope):
    """Represents the scope of bot commands, covering all administrators of a specific group or
    supergroup chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type` and :attr:`chat_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.CHAT_ADMINISTRATORS`.
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)
    """

    __slots__ = ('chat_id',)

    def __init__(self, chat_id: Union[str, int], **_kwargs: Any):
        super().__init__(type=BotCommandScope.CHAT_ADMINISTRATORS)
        self.chat_id = (
            chat_id if isinstance(chat_id, str) and chat_id.startswith('@') else int(chat_id)
        )
        self._id_attrs = (self.type, self.chat_id)


class BotCommandScopeChatMember(BotCommandScope):
    """Represents the scope of bot commands, covering a specific member of a group or supergroup
    chat.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`type`, :attr:`chat_id` and :attr:`user_id` are equal.

    .. versionadded:: 13.7

    Args:
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)
        user_id (:obj:`int`): Unique identifier of the target user.

    Attributes:
        type (:obj:`str`): Scope type :attr:`telegram.BotCommandScope.CHAT_MEMBER`.
        chat_id (:obj:`str` | :obj:`int`): Unique identifier for the target chat or username of the
            target supergroup (in the format ``@supergroupusername``)
        user_id (:obj:`int`): Unique identifier of the target user.
    """

    __slots__ = ('chat_id', 'user_id')

    def __init__(self, chat_id: Union[str, int], user_id: int, **_kwargs: Any):
        super().__init__(type=BotCommandScope.CHAT_MEMBER)
        self.chat_id = (
            chat_id if isinstance(chat_id, str) and chat_id.startswith('@') else int(chat_id)
        )
        self.user_id = int(user_id)
        self._id_attrs = (self.type, self.chat_id, self.user_id)
