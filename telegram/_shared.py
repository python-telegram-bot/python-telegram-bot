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
"""This module contains two objects used for request chats/users service messages."""
from typing import Optional, Sequence, Tuple

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict
from telegram._utils.warnings import warn
from telegram._utils.warnings_transition import (
    build_deprecation_warning_message,
    warn_about_deprecated_attr_in_property,
)
from telegram.warnings import PTBDeprecationWarning


class UsersShared(TelegramObject):
    """
    This object contains information about the user whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestUsers` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`user_ids` are equal.

    .. versionadded:: 20.8
       Bot API 7.0 replaces :class:`UserShared` with this class. The only difference is that now
       the :attr:`user_ids` is a sequence instead of a single integer.

    Args:
        request_id (:obj:`int`): Identifier of the request.
        user_ids (Sequence[:obj:`int`]): Identifiers of the shared users. These numbers may have
            more than 32 significant bits and some programming languages may have difficulty/silent
            defects in interpreting them. But they have at most 52 significant bits, so 64-bit
            integers or double-precision float types are safe for storing these identifiers. The
            bot may not have access to the users and could be unable to use these identifiers,
            unless the users are already known to the bot by some other means.

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        user_ids (Tuple[:obj:`int`]): Identifiers of the shared users. These numbers may have
            more than 32 significant bits and some programming languages may have difficulty/silent
            defects in interpreting them. But they have at most 52 significant bits, so 64-bit
            integers or double-precision float types are safe for storing these identifiers. The
            bot may not have access to the users and could be unable to use these identifiers,
            unless the users are already known to the bot by some other means.
    """

    __slots__ = ("request_id", "user_ids")

    def __init__(
        self,
        request_id: int,
        user_ids: Sequence[int],
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.request_id: int = request_id
        self.user_ids: Tuple[int, ...] = tuple(user_ids)

        self._id_attrs = (self.request_id, self.user_ids)

        self._freeze()


class UserShared(UsersShared):
    """Alias for :class:`UsersShared`, kept for backward compatibility.

    .. versionadded:: 20.1

    .. deprecated:: 20.8
        Use :class:`UsersShared` instead.

    """

    __slots__ = ()

    def __init__(
        self,
        request_id: int,
        user_id: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(request_id, (user_id,), api_kwargs=api_kwargs)

        warn(
            build_deprecation_warning_message(
                deprecated_name="UserShared",
                new_name="UsersShared",
                object_type="class",
                bot_api_version="7.0",
            ),
            PTBDeprecationWarning,
            stacklevel=2,
        )

        self._freeze()

    @property
    def user_id(self) -> int:
        """Alias for the first entry of :attr:`UsersShared.user_ids`.

        .. deprecated:: 20.8
           Bot API 7.0 deprecates this attribute in favor of :attr:`UsersShared.user_ids`.
        """
        warn_about_deprecated_attr_in_property(
            deprecated_attr_name="user_id",
            new_attr_name="user_ids",
            bot_api_version="7.0",
        )
        return self.user_ids[0]


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

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        chat_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
    """

    __slots__ = ("chat_id", "request_id")

    def __init__(
        self,
        request_id: int,
        chat_id: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.request_id: int = request_id
        self.chat_id: int = chat_id

        self._id_attrs = (self.request_id, self.chat_id)

        self._freeze()
