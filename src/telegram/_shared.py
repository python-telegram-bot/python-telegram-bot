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
"""This module contains two objects used for request chats/users service messages."""

from telegram._files.photosize import PhotoSize
from telegram._telegramobject import TelegramObject
from telegram._utils.argumentparsing import parse_sequence_arg
from telegram._utils.dataclass import tg_dataclass, tg_field
from telegram._utils.usernames import get_full_name, get_link, get_name


@tg_dataclass()
class UsersShared(TelegramObject):
    """
    This object contains information about the user whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestUsers` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`users` are equal.

    .. versionadded:: 20.8
       Bot API 7.0 replaces ``UserShared`` with this class. The only difference is that now
       the ``user_ids`` is a sequence instead of a single integer.

    .. versionchanged:: 21.1
       The argument :attr:`users` is now considered for the equality comparison instead of
       ``user_ids``.

    .. versionremoved:: 21.2
       Removed the deprecated argument and attribute ``user_ids``.

    Args:
        request_id (:obj:`int`): Identifier of the request.
        users (Sequence[:class:`telegram.SharedUser`]): Information about users shared with the
            bot.

            .. versionadded:: 21.1

            .. versionchanged:: 21.2
               This argument is now required.

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        users (tuple[:class:`telegram.SharedUser`]): Information about users shared with the
            bot.

            .. versionadded:: 21.1
    """

    __REMOVED_API_FIELDS__ = frozenset(
        {
            "user_ids",
        }
    )

    request_id: int = tg_field(compare=True)
    users: tuple["SharedUser", ...] = tg_field(compare=True, converter=parse_sequence_arg)


@tg_dataclass()
class ChatShared(TelegramObject):
    """
    This object contains information about the chat whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestChat` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`chat_id` are equal.

    .. versionadded:: 20.1

    Args:
        request_id (:obj:`int`): Identifier of the request.
        chat_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
        title (:obj:`str`, optional): Title of the chat, if the title was requested by the bot.

            .. versionadded:: 21.1
        username (:obj:`str`, optional): Username of the chat, if the username was requested by
            the bot and available.

            .. versionadded:: 21.1
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Available sizes of the chat photo,
            if the photo was requested by the bot

            .. versionadded:: 21.1

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        chat_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
        title (:obj:`str`): Optional. Title of the chat, if the title was requested by the bot.

            .. versionadded:: 21.1
        username (:obj:`str`): Optional. Username of the chat, if the username was requested by
            the bot and available.

            .. versionadded:: 21.1
        photo (tuple[:class:`telegram.PhotoSize`]): Optional. Available sizes of the chat photo,
            if the photo was requested by the bot

            .. versionadded:: 21.1
    """

    # Required
    request_id: int = tg_field(compare=True)
    chat_id: int = tg_field(compare=True)
    # Optional
    title: str | None = tg_field(default=None)
    username: str | None = tg_field(default=None)
    photo: tuple[PhotoSize, ...] = tg_field(default=None, converter=parse_sequence_arg)

    @property
    def link(self) -> str | None:
        """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
        of the chat.

        .. versionadded:: 22.4
        """
        return get_link(self)


@tg_dataclass()
class SharedUser(TelegramObject):
    """
    This object contains information about a user that was shared with the bot using a
    :class:`telegram.KeyboardButtonRequestUsers` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`user_id` is equal.

    .. versionadded:: 21.1

    Args:
        user_id (:obj:`int`): Identifier of the shared user. This number may have 32 significant
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it has atmost 52 significant bits, so 64-bit integers or double-precision
            float types are safe for storing these identifiers. The bot may not have access to the
            user and could be unable to use this identifier, unless the user is already known to
            the bot by some other means.
        first_name (:obj:`str`, optional): First name of the user, if the name was requested by the
            bot.
        last_name (:obj:`str`, optional): Last name of the user, if the name was requested by the
            bot.
        username (:obj:`str`, optional): Username of the user, if the username was requested by the
            bot.
        photo (Sequence[:class:`telegram.PhotoSize`], optional): Available sizes of the chat photo,
            if the photo was requested by the bot.

    Attributes:
        user_id (:obj:`int`): Identifier of the shared user. This number may have 32 significant
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it has atmost 52 significant bits, so 64-bit integers or double-precision
            float types are safe for storing these identifiers. The bot may not have access to the
            user and could be unable to use this identifier, unless the user is already known to
            the bot by some other means.
        first_name (:obj:`str`): Optional. First name of the user, if the name was requested by the
            bot.
        last_name (:obj:`str`): Optional. Last name of the user, if the name was requested by the
            bot.
        username (:obj:`str`): Optional. Username of the user, if the username was requested by the
            bot.
        photo (tuple[:class:`telegram.PhotoSize`]): Available sizes of the chat photo, if
            the photo was requested by the bot. This list is empty if the photo was not requsted.
    """

    # Required
    user_id: int = tg_field(compare=True)
    # Optional
    first_name: str | None = tg_field(default=None)
    last_name: str | None = tg_field(default=None)
    username: str | None = tg_field(default=None)
    photo: tuple[PhotoSize, ...] = tg_field(default=None, converter=parse_sequence_arg)

    @property
    def name(self) -> str | None:
        """:obj:`str`: Convenience property. If available, returns the user's :attr:`username`
        prefixed with "@". If :attr:`username` is not available, returns :attr:`full_name`.

        .. versionadded:: 22.4
        """
        return get_name(self)

    @property
    def full_name(self) -> str | None:
        """:obj:`str`: Convenience property. If :attr:`first_name` is not :obj:`None`, gives
        :attr:`first_name` followed by (if available) :attr:`last_name`.

        .. versionadded:: 22.4
        """
        return get_full_name(self)

    @property
    def link(self) -> str | None:
        """:obj:`str`: Convenience property. If :attr:`username` is available, returns a t.me link
        of the user.

        .. versionadded:: 22.4
        """
        return get_link(self)
