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
# TODO: Remove allow_edited
"""This module contains the RegexHandler class."""

import warnings
from typing import TYPE_CHECKING, Callable, Dict, Optional, Pattern, TypeVar, Union, Any

from telegram import Update
from telegram.ext import Filters, MessageHandler
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.utils.helpers import DefaultValue, DEFAULT_FALSE
from telegram.ext.utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class RegexHandler(MessageHandler):
    """Handler class to handle Telegram updates based on a regex.

    It uses a regular expression to check text messages. Read the documentation of the ``re``
    module for more information. The ``re.match`` function is used to determine if an update should
    be handled by this handler.

    Note:
        This handler is being deprecated. For the same use case use:
        ``MessageHandler(Filters.regex(r'pattern'), callback)``

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.


    Args:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is :obj:`False`
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is :obj:`False`
        pass_update_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is :obj:`False`.
        pass_job_queue (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is :obj:`False`.
        pass_user_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is :obj:`False`.
        pass_chat_data (:obj:`bool`, optional): If set to :obj:`True`, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is :obj:`False`.
        message_updates (:obj:`bool`, optional): Should "normal" message updates be handled?
            Default is :obj:`True`.
        channel_post_updates (:obj:`bool`, optional): Should channel posts updates be handled?
            Default is :obj:`True`.
        edited_updates (:obj:`bool`, optional): Should "edited" message updates be handled? Default
            is :obj:`False`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Raises:
        ValueError

    Attributes:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler.
        pass_groups (:obj:`bool`): Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Determines whether ``groupdict``. will be passed to
            the callback function.
        pass_update_queue (:obj:`bool`): Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Determines whether ``job_queue`` will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Determines whether ``chat_data`` will be passed to
            the callback function.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('pass_groups', 'pass_groupdict')

    def __init__(
        self,
        pattern: Union[str, Pattern],
        callback: Callable[[Update, CCT], RT],
        pass_groups: bool = False,
        pass_groupdict: bool = False,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = False,
        pass_chat_data: bool = False,
        allow_edited: bool = False,  # pylint: disable=W0613
        message_updates: bool = True,
        channel_post_updates: bool = False,
        edited_updates: bool = False,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        warnings.warn(
            'RegexHandler is deprecated. See '
            'https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to'
            '-Version-12.0 for more info',
            TelegramDeprecationWarning,
            stacklevel=2,
        )
        super().__init__(
            Filters.regex(pattern),
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            message_updates=message_updates,
            channel_post_updates=channel_post_updates,
            edited_updates=edited_updates,
            run_async=run_async,
        )
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def collect_optional_args(
        self,
        dispatcher: 'Dispatcher',
        update: Update = None,
        check_result: Optional[Union[bool, Dict[str, Any]]] = None,
    ) -> Dict[str, object]:
        """Pass the results of ``re.match(pattern, text).{groups(), groupdict()}`` to the
        callback as a keyword arguments called ``groups`` and ``groupdict``, respectively, if
        needed.
        """
        optional_args = super().collect_optional_args(dispatcher, update, check_result)
        if isinstance(check_result, dict):
            if self.pass_groups:
                optional_args['groups'] = check_result['matches'][0].groups()
            if self.pass_groupdict:
                optional_args['groupdict'] = check_result['matches'][0].groupdict()
        return optional_args
