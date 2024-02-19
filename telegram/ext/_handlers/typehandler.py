#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
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
"""This module contains the TypeHandler class."""

from typing import Optional, Type, TypeVar

from telegram._utils.defaultvalue import DEFAULT_TRUE
from telegram._utils.types import DVType
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext._utils.types import CCT, HandlerCallback

RT = TypeVar("RT")
UT = TypeVar("UT")


class TypeHandler(BaseHandler[UT, CCT]):
    """Handler class to handle updates of custom types.

    Warning:
        When setting :paramref:`block` to :obj:`False`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        type (:external:class:`type`): The :external:class:`type` of updates this handler should
            process, as determined by :obj:`isinstance`
        callback (:term:`coroutine function`): The callback function for this handler. Will be
            called when :meth:`check_update` has determined that an update should be processed by
            this handler. Callback signature::

                async def callback(update: Update, context: CallbackContext)

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        strict (:obj:`bool`, optional): Use ``type`` instead of :obj:`isinstance`.
            Default is :obj:`False`.
        block (:obj:`bool`, optional): Determines whether the return value of the callback should
            be awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`. Defaults to :obj:`True`.

            .. seealso:: :wiki:`Concurrency`

    Attributes:
        type (:external:class:`type`): The :external:class:`type` of updates this handler should
            process.
        callback (:term:`coroutine function`): The callback function for this handler.
        strict (:obj:`bool`): Use :external:class:`type` instead of :obj:`isinstance`. Default is
            :obj:`False`.
        block (:obj:`bool`): Determines whether the return value of the callback should be
            awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`.

    """

    __slots__ = ("strict", "type")

    def __init__(
        self,
        type: Type[UT],  # pylint: disable=redefined-builtin
        callback: HandlerCallback[UT, CCT, RT],
        strict: bool = False,
        block: DVType[bool] = DEFAULT_TRUE,
    ):
        super().__init__(callback, block=block)
        self.type: Type[UT] = type
        self.strict: Optional[bool] = strict

    def check_update(self, update: object) -> bool:
        """Determines whether an update should be passed to this handler's :attr:`callback`.

        Args:
            update (:obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if not self.strict:
            return isinstance(update, self.type)
        return type(update) is self.type  # pylint: disable=unidiomatic-typecheck
