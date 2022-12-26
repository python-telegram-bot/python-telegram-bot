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
"""This module contains the ChatMemberHandler class."""
from typing import ClassVar, TypeVar

from telegram import Update
from telegram._utils.defaultvalue import DEFAULT_TRUE
from telegram._utils.types import DVInput
from telegram.ext._handler import BaseHandler
from telegram.ext._utils.types import CCT, HandlerCallback

RT = TypeVar("RT")


class ChatMemberHandler(BaseHandler[Update, CCT]):
    """BaseHandler class to handle Telegram updates that contain a chat member update.

    Warning:
        When setting :paramref:`block` to :obj:`False`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Examples:
        :any:`Chat Member Bot <examples.chatmemberbot>`

    .. versionadded:: 13.4

    Args:
        callback (:term:`coroutine function`): The callback function for this handler. Will be
            called when :meth:`check_update` has determined that an update should be processed by
            this handler. Callback signature::

                async def callback(update: Update, context: CallbackContext)

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        chat_member_types (:obj:`int`, optional): Pass one of :attr:`MY_CHAT_MEMBER`,
            :attr:`CHAT_MEMBER` or :attr:`ANY_CHAT_MEMBER` to specify if this handler should handle
            only updates with :attr:`telegram.Update.my_chat_member`,
            :attr:`telegram.Update.chat_member` or both. Defaults to :attr:`MY_CHAT_MEMBER`.
        block (:obj:`bool`, optional): Determines whether the return value of the callback should
            be awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`. Defaults to :obj:`True`.

            .. seealso:: :wiki:`Concurrency`

    Attributes:
        callback (:term:`coroutine function`): The callback function for this handler.
        chat_member_types (:obj:`int`): Optional. Specifies if this handler should handle
            only updates with :attr:`telegram.Update.my_chat_member`,
            :attr:`telegram.Update.chat_member` or both.
        block (:obj:`bool`): Determines whether the return value of the callback should be
            awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`.

    """

    __slots__ = ("chat_member_types",)
    MY_CHAT_MEMBER: ClassVar[int] = -1
    """:obj:`int`: Used as a constant to handle only :attr:`telegram.Update.my_chat_member`."""
    CHAT_MEMBER: ClassVar[int] = 0
    """:obj:`int`: Used as a constant to handle only :attr:`telegram.Update.chat_member`."""
    ANY_CHAT_MEMBER: ClassVar[int] = 1
    """:obj:`int`: Used as a constant to handle both :attr:`telegram.Update.my_chat_member`
    and :attr:`telegram.Update.chat_member`."""

    def __init__(
        self,
        callback: HandlerCallback[Update, CCT, RT],
        chat_member_types: int = MY_CHAT_MEMBER,
        block: DVInput[bool] = DEFAULT_TRUE,
    ):
        super().__init__(callback, block=block)

        self.chat_member_types = chat_member_types

    def check_update(self, update: object) -> bool:
        """Determines whether an update should be passed to this handler's :attr:`callback`.

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
