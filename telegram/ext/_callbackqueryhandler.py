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
"""This module contains the CallbackQueryHandler class."""

import re
from typing import (
    TYPE_CHECKING,
    Callable,
    Match,
    Optional,
    Pattern,
    TypeVar,
    Union,
    cast,
)

from telegram import Update
from telegram.ext import Handler
from telegram._utils.defaultvalue import DefaultValue, DEFAULT_FALSE
from telegram.ext._utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class CallbackQueryHandler(Handler[Update, CCT]):
    """Handler class to handle Telegram callback queries. Optionally based on a regex.

    Read the documentation of the ``re`` module for more information.

    Note:
        * If your bot allows arbitrary objects as ``callback_data``, it may happen that the
          original ``callback_data`` for the incoming :class:`telegram.CallbackQuery`` can not be
          found. This is the case when either a malicious client tempered with the
          ``callback_data`` or the data was simply dropped from cache or not persisted. In these
          cases, an instance of :class:`telegram.ext.InvalidCallbackData` will be set as
          ``callback_data``.

          .. versionadded:: 13.6

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pattern (:obj:`str` | `Pattern` | :obj:`callable` | :obj:`type`, optional):
            Pattern to test :attr:`telegram.CallbackQuery.data` against. If a string or a regex
            pattern is passed, :meth:`re.match` is used on :attr:`telegram.CallbackQuery.data` to
            determine if an update should be handled by this handler. If your bot allows arbitrary
            objects as ``callback_data``, non-strings will be accepted. To filter arbitrary
            objects you may pass

                * a callable, accepting exactly one argument, namely the
                  :attr:`telegram.CallbackQuery.data`. It must return :obj:`True` or
                  :obj:`False`/:obj:`None` to indicate, whether the update should be handled.
                * a :obj:`type`. If :attr:`telegram.CallbackQuery.data` is an instance of that type
                  (or a subclass), the update will be handled.

            If :attr:`telegram.CallbackQuery.data` is :obj:`None`, the
            :class:`telegram.CallbackQuery` update will not be handled.

            .. versionchanged:: 13.6
               Added support for arbitrary callback data.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pattern (`Pattern` | :obj:`callable` | :obj:`type`): Optional. Regex pattern, callback or
            type to test :attr:`telegram.CallbackQuery.data` against.

            .. versionchanged:: 13.6
               Added support for arbitrary callback data.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('pattern',)

    def __init__(
        self,
        callback: Callable[[Update, CCT], RT],
        pattern: Union[str, Pattern, type, Callable[[object], Optional[bool]]] = None,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern

    def check_update(self, update: object) -> Optional[Union[bool, object]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update) and update.callback_query:
            callback_data = update.callback_query.data
            if self.pattern:
                if callback_data is None:
                    return False
                if isinstance(self.pattern, type):
                    return isinstance(callback_data, self.pattern)
                if callable(self.pattern):
                    return self.pattern(callback_data)
                match = re.match(self.pattern, callback_data)
                if match:
                    return match
            else:
                return True
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: Union[bool, Match],
    ) -> None:
        """Add the result of ``re.match(pattern, update.callback_query.data)`` to
        :attr:`CallbackContext.matches` as list with one element.
        """
        if self.pattern:
            check_result = cast(Match, check_result)
            context.matches = [check_result]
