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
from typing import Optional

from telegram._telegramobject import TelegramObject
from telegram._utils.types import JSONDict


class UserShared(TelegramObject):
    """
    This object contains information about the user whose identifier was shared with the bot
    using a :class:`telegram.KeyboardButtonRequestUser` button.

    Objects of this class are comparable in terms of equality. Two objects of this class are
    considered equal, if their :attr:`request_id` and :attr:`user_id` are equal.

    .. versionadded:: 20.1

    Args:
        request_id (:obj:`int`): Identifier of the request.
        user_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.

    Attributes:
        request_id (:obj:`int`): Identifier of the request.
        user_id (:obj:`int`): Identifier of the shared user. This number may be greater than 32
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it is smaller than 52 bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
    """

    __slots__ = ("request_id", "user_id")

    def __init__(
        self,
        request_id: int,
        user_id: int,
        *,
        api_kwargs: Optional[JSONDict] = None,
    ):
        super().__init__(api_kwargs=api_kwargs)
        self.request_id: int = request_id
        self.user_id: int = user_id

        self._id_attrs = (self.request_id, self.user_id)

        self._freeze()


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

    __slots__ = ("request_id", "chat_id")

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
