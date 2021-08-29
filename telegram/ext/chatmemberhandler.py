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
"""This module contains the ChatMemberHandler classes."""
from typing import ClassVar, TypeVar, Union, Callable

from telegram import Update
from telegram.utils.helpers import DefaultValue, DEFAULT_FALSE
from .handler import Handler
from .utils.types import CCT

RT = TypeVar('RT')


class ChatMemberHandler(Handler[Update, CCT]):
    """Handler class to handle Telegram updates that contain a chat member update.

    .. versionadded:: 13.4

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        chat_member_types (:obj:`int`, optional): Pass one of :attr:`MY_CHAT_MEMBER`,
            :attr:`CHAT_MEMBER` or :attr:`ANY_CHAT_MEMBER` to specify if this handler should handle
            only updates with :attr:`telegram.Update.my_chat_member`,
            :attr:`telegram.Update.chat_member` or both. Defaults to :attr:`MY_CHAT_MEMBER`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        chat_member_types (:obj:`int`, optional): Specifies if this handler should handle
            only updates with :attr:`telegram.Update.my_chat_member`,
            :attr:`telegram.Update.chat_member` or both.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('chat_member_types',)
    MY_CHAT_MEMBER: ClassVar[int] = -1
    """:obj:`int`: Used as a constant to handle only :attr:`telegram.Update.my_chat_member`."""
    CHAT_MEMBER: ClassVar[int] = 0
    """:obj:`int`: Used as a constant to handle only :attr:`telegram.Update.chat_member`."""
    ANY_CHAT_MEMBER: ClassVar[int] = 1
    """:obj:`int`: Used as a constant to handle bot :attr:`telegram.Update.my_chat_member`
    and :attr:`telegram.Update.chat_member`."""

    def __init__(
        self,
        callback: Callable[[Update, CCT], RT],
        chat_member_types: int = MY_CHAT_MEMBER,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )

        self.chat_member_types = chat_member_types

    def check_update(self, update: object) -> bool:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update):
            if not (update.my_chat_member or update.chat_member):
                return False
            if self.chat_member_types == self.ANY_CHAT_MEMBER:
                return True
            if self.chat_member_types == self.CHAT_MEMBER:
                return bool(update.chat_member)
            return bool(update.my_chat_member)
        return False
