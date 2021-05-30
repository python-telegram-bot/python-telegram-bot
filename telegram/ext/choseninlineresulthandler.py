#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
"""This module contains the ChosenInlineResultHandler class."""
import re
from typing import Optional, TypeVar, Union, Callable, TYPE_CHECKING, Pattern, Match, cast

from telegram import Update

from telegram.utils.helpers import DefaultValue, DEFAULT_FALSE
from .handler import Handler
from .utils.types import CCT

RT = TypeVar('RT')

if TYPE_CHECKING:
    from telegram.ext import CallbackContext, Dispatcher


class ChosenInlineResultHandler(Handler[Update, CCT]):
    """Handler class to handle Telegram updates that contain a chosen inline result.

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
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
            DEPRECATED: Please switch to context based callbacks.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.
        pattern (:obj:`str` | `Pattern`, optional): Regex pattern. If not :obj:`None`, ``re.match``
            is used on :attr:`telegram.ChosenInlineResult.result_id` to determine if an update
            should be handled by this handler. This is accessible in the callback as
            :attr:`telegram.ext.CallbackContext.matches`.

            .. versionadded:: 13.6

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
        pattern (`Pattern`): Optional. Regex pattern to test
            :attr:`telegram.ChosenInlineResult.result_id` against.

            .. versionadded:: 13.6

    """

    __slots__ = ('pattern',)

    def __init__(
        self,
        callback: Callable[[Update, 'CallbackContext'], RT],
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = False,
        pass_chat_data: bool = False,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
        pattern: Union[str, Pattern] = None,
    ):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
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
        if isinstance(update, Update) and update.chosen_inline_result:
            if self.pattern:
                match = re.match(self.pattern, update.chosen_inline_result.result_id)
                if match:
                    return match
            else:
                return True
        return None

    def collect_additional_context(
        self,
        context: 'CallbackContext',
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: Union[bool, Match],
    ) -> None:
        """This function adds the matched regex pattern result to
        :attr:`telegram.ext.CallbackContext.matches`.
        """
        if self.pattern:
            check_result = cast(Match, check_result)
            context.matches = [check_result]
