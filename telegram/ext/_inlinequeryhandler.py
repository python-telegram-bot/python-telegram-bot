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
"""This module contains the InlineQueryHandler class."""
import re
from typing import TYPE_CHECKING, Any, List, Match, Optional, Pattern, TypeVar, Union, cast

from telegram import Update
from telegram._utils.defaultvalue import DEFAULT_TRUE
from telegram._utils.types import DVType
from telegram.ext._handler import BaseHandler
from telegram.ext._utils.types import CCT, HandlerCallback

if TYPE_CHECKING:
    from telegram.ext import Application

RT = TypeVar("RT")


class InlineQueryHandler(BaseHandler[Update, CCT]):
    """
    BaseHandler class to handle Telegram updates that contain a
    :attr:`telegram.Update.inline_query`.
    Optionally based on a regex. Read the documentation of the :mod:`re` module for more
    information.

    Warning:
        * When setting :paramref:`block` to :obj:`False`, you cannot rely on adding custom
          attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.
        * :attr:`telegram.InlineQuery.chat_type` will not be set for inline queries from secret
          chats and may not be set for inline queries coming from third-party clients. These
          updates won't be handled, if :attr:`chat_types` is passed.

    Examples:
        :any:`Inline Bot <examples.inlinebot>`


    Args:
        callback (:term:`coroutine function`): The callback function for this handler. Will be
            called when :meth:`check_update` has determined that an update should be processed by
            this handler. Callback signature::

                async def callback(update: Update, context: CallbackContext)

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pattern (:obj:`str` | :func:`re.Pattern <re.compile>`, optional): Regex pattern.
            If not :obj:`None`, :func:`re.match` is used on :attr:`telegram.InlineQuery.query`
            to determine if an update should be handled by this handler.
        block (:obj:`bool`, optional): Determines whether the return value of the callback should
            be awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`. Defaults to :obj:`True`.

            .. seealso:: :wiki:`Concurrency`
        chat_types (List[:obj:`str`], optional): List of allowed chat types. If passed, will only
            handle inline queries with the appropriate :attr:`telegram.InlineQuery.chat_type`.

            .. versionadded:: 13.5
    Attributes:
        callback (:term:`coroutine function`): The callback function for this handler.
        pattern (:obj:`str` | :func:`re.Pattern <re.compile>`): Optional. Regex pattern to test
            :attr:`telegram.InlineQuery.query` against.
        chat_types (List[:obj:`str`]): Optional. List of allowed chat types.

            .. versionadded:: 13.5
        block (:obj:`bool`): Determines whether the return value of the callback should be
            awaited before processing the next handler in
            :meth:`telegram.ext.Application.process_update`.

    """

    __slots__ = ("pattern", "chat_types")

    def __init__(
        self,
        callback: HandlerCallback[Update, CCT, RT],
        pattern: Optional[Union[str, Pattern[str]]] = None,
        block: DVType[bool] = DEFAULT_TRUE,
        chat_types: Optional[List[str]] = None,
    ):
        super().__init__(callback, block=block)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern: Optional[Union[str, Pattern[str]]] = pattern
        self.chat_types: Optional[List[str]] = chat_types

    def check_update(self, update: object) -> Optional[Union[bool, Match[str]]]:
        """
        Determines whether an update should be passed to this handler's :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool` | :obj:`re.match`

        """
        if isinstance(update, Update) and update.inline_query:
            if (self.chat_types is not None) and (
                update.inline_query.chat_type not in self.chat_types
            ):
                return False
            if self.pattern:
                if update.inline_query.query:
                    match = re.match(self.pattern, update.inline_query.query)
                    if match:
                        return match
            else:
                return True
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,  # skipcq: BAN-B301
        application: "Application[Any, CCT, Any, Any, Any, Any]",  # skipcq: BAN-B301
        check_result: Optional[Union[bool, Match[str]]],
    ) -> None:
        """Add the result of ``re.match(pattern, update.inline_query.query)`` to
        :attr:`CallbackContext.matches` as list with one element.
        """
        if self.pattern:
            check_result = cast(Match, check_result)
            context.matches = [check_result]
