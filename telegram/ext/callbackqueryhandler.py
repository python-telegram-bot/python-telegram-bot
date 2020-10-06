#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
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

from telegram import Update
from .handler import Handler

from telegram.utils.types import HandlerArg
from typing import Callable, TYPE_CHECKING, Any, Optional, Union, TypeVar, Pattern, Match, Dict, \
    cast

if TYPE_CHECKING:
    from telegram.ext import CallbackContext, Dispatcher

RT = TypeVar('RT')


class CallbackQueryHandler(Handler):
    """Handler class to handle Telegram callback queries. Optionally based on a regex.

    Read the documentation of the ``re`` module for more information.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pattern (:obj:`str` | `Pattern`): Optional. Regex pattern to test
            :attr:`telegram.CallbackQuery.data` against.
        pass_groups (:obj:`bool`): Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Determines whether ``groupdict``. will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

        Note that this is DEPRECATED, and you should use context based callbacks. See
        https://git.io/fxJuV for more info.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

                ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_update_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_job_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pattern (:obj:`str` | `Pattern`, optional): Regex pattern. If not :obj:`None`, ``re.match``
            is used on :attr:`telegram.CallbackQuery.data` to determine if an update should be
            handled by this handler.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is :obj:`False`
            DEPRECATED: Please switch to context based callbacks.
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is :obj:`False`
            DEPRECATED: Please switch to context based callbacks.
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    """

    def __init__(self,
                 callback: Callable[[HandlerArg, 'CallbackContext'], RT],
                 pass_update_queue: bool = False,
                 pass_job_queue: bool = False,
                 pattern: Union[str, Pattern] = None,
                 pass_groups: bool = False,
                 pass_groupdict: bool = False,
                 pass_user_data: bool = False,
                 pass_chat_data: bool = False,
                 run_async: bool = False):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, update: HandlerArg) -> Optional[Union[bool, object]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update) and update.callback_query:
            if self.pattern:
                if update.callback_query.data:
                    match = re.match(self.pattern, update.callback_query.data)
                    if match:
                        return match
            else:
                return True
        return None

    def collect_optional_args(self,
                              dispatcher: 'Dispatcher',
                              update: HandlerArg = None,
                              check_result: Union[bool, Match] = None) -> Dict[str, Any]:
        optional_args = super().collect_optional_args(dispatcher, update, check_result)
        if self.pattern:
            check_result = cast(Match, check_result)
            if self.pass_groups:
                optional_args['groups'] = check_result.groups()
            if self.pass_groupdict:
                optional_args['groupdict'] = check_result.groupdict()
        return optional_args

    def collect_additional_context(self,
                                   context: 'CallbackContext',
                                   update: HandlerArg,
                                   dispatcher: 'Dispatcher',
                                   check_result: Union[bool, Match]) -> None:
        if self.pattern:
            check_result = cast(Match, check_result)
            context.matches = [check_result]
