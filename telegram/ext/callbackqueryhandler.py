#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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

from future.utils import string_types

from telegram import Update
from .handler import Handler


class CallbackQueryHandler(Handler):
    """Handler class to handle Telegram callback queries. Optionally based on a regex.

    Read the documentation of the ``re`` module for more information.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.
        pattern (:obj:`str` | `Pattern`): Optional. Regex pattern to test
            :attr:`telegram.CallbackQuery.data` against.
        pass_groups (:obj:`bool`): Optional. Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Optional. Determines whether ``groupdict``. will be passed to
            the callback function.
        pass_user_data (:obj:`bool`): Optional. Determines whether ``user_data`` will be passed to
            the callback function.
        pass_chat_data (:obj:`bool`): Optional. Determines whether ``chat_data`` will be passed to
            the callback function.
        use_context (:obj:`bool`): Optional. Determines whether all `pass_` arguments will be
            ignored in favor of passing a :class:`telegram.ext.Context` object to the callback.

    Note:
        :attr:`pass_user_data` and :attr:`pass_chat_data` determine whether a ``dict`` you
        can use to keep any data in will be sent to the :attr:`callback` function.. Related to
        either the user or the chat that the update was sent in. For each update from the same user
        or in the same chat, it will be the same ``dict``.

    Note:
        Instead of using the individual `pass_` you can use :attr:`use_context` and your callback
        function will receive a :class:`telegram.ext.Context` object as the only parameter,
        instead of the usual (bot, update, others...).

    Args:
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.
        pattern (:obj:`str` | `Pattern`, optional): Regex pattern. If not ``None``, ``re.match``
            is used on :attr:`telegram.CallbackQuery.data` to determine if an update should be
            handled by this handler.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is ``False``
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is ``False``
        pass_user_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. Default is ``False``.
        pass_chat_data (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. Default is ``False``.
        use_context (:obj:`bool`, optional): If set to ``True``, all `pass_` arguments will be
            ignored in favor of passing a :class:`telegram.ext.Context` object to the callback.
            Defaults to ``True`` if :attr:`callback` has only one parameter. Note that this can
            be difficult to determine if :attr:`callback` is decorated - especially on python 2.

    """

    def __init__(self,
                 callback,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pattern=None,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_user_data=False,
                 pass_chat_data=False,
                 use_context=None):
        super(CallbackQueryHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            use_context=use_context)

        if isinstance(pattern, string_types):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, update):
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
                    return bool(match)
            else:
                return True

    def collect_optional_args(self, dispatcher, update=None):
        optional_args = super(CallbackQueryHandler, self).collect_optional_args(dispatcher, update)
        if self.pattern:
            match = re.match(self.pattern, update.callback_query.data)

            if self.pass_groups:
                optional_args['groups'] = match.groups()
            if self.pass_groupdict:
                optional_args['groupdict'] = match.groupdict()
        return optional_args

    def collect_additional_context(self, context, update, dispatcher):
        if self.pattern:
            match = re.match(self.pattern, update.callback_query.data)

            context.groups = match.groups()
            context.groupdict = match.groupdict()
