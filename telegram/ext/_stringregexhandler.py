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
"""This module contains the StringRegexHandler class."""

import re
from typing import TYPE_CHECKING, Callable, Match, Optional, Pattern, TypeVar, Union

from telegram.ext import Handler
from telegram.ext._utils.types import CCT
from telegram._utils.defaultvalue import DefaultValue, DEFAULT_FALSE

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class StringRegexHandler(Handler[str, CCT]):
    """Handler class to handle string updates based on a regex which checks the update content.

    Read the documentation of the :mod:`re` module for more information. The :func:`re.match`
    function is used to determine if an update should be handled by this handler.

    Note:
        This handler is not used to handle Telegram :attr:`telegram.Update`, but strings manually
        put in the queue. For example to send messages with the bot using command line or API.

    Warning:
        When setting :paramref:`run_async` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        pattern (:obj:`str` | :func:`re.Pattern <re.compile>`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        pattern (:obj:`str` | :func:`re.Pattern <re.compile>`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('pattern',)

    def __init__(
        self,
        pattern: Union[str, Pattern],
        callback: Callable[[str, CCT], RT],
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern

    def check_update(self, update: object) -> Optional[Match]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`object`): The incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, str):
            match = re.match(self.pattern, update)
            if match:
                return match
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: str,
        dispatcher: 'Dispatcher',
        check_result: Optional[Match],
    ) -> None:
        """Add the result of ``re.match(pattern, update)`` to :attr:`CallbackContext.matches` as
        list with one element.
        """
        if self.pattern and check_result:
            context.matches = [check_result]
