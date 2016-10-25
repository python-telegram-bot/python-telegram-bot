#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
""" This module contains the RegexHandler class """

import re

from future.utils import string_types

from .handler import Handler
from telegram import Update
from telegram.utils.deprecate import deprecate


class RegexHandler(Handler):
    """
    Handler class to handle Telegram updates based on a regex. It uses a
    regular expression to check text messages. Read the documentation of the
    ``re`` module for more information. The ``re.match`` function is used to
    determine if an update should be handled by this handler.

    Args:
        pattern (str or Pattern): The regex pattern.
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        pass_groups (optional[bool]): If the callback should be passed the
            result of ``re.match(pattern, text).groups()`` as a keyword
            argument called ``groups``. Default is ``False``
        pass_groupdict (optional[bool]): If the callback should be passed the
            result of ``re.match(pattern, text).groupdict()`` as a keyword
            argument called ``groupdict``. Default is ``False``
        pass_update_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the ``Updater`` and ``Dispatcher`` that contains new updates which can
             be used to insert updates. Default is ``False``.
        pass_job_queue (optional[bool]): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a ``JobQueue``
            instance created by the ``Updater`` which can be used to schedule new jobs.
            Default is ``False``.
        pass_user_data (optional[bool]): If set to ``True``, a keyword argument called
            ``user_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the user that sent the update. For each update of
            the same user, it will be the same ``dict``. Default is ``False``.
        pass_chat_data (optional[bool]): If set to ``True``, a keyword argument called
            ``chat_data`` will be passed to the callback function. It will be a ``dict`` you
            can use to keep any data related to the chat that the update was sent in.
            For each update in the same chat, it will be the same ``dict``. Default is ``False``.
    """

    def __init__(self,
                 pattern,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False,
                 pass_user_data=False,
                 pass_chat_data=False):
        super(RegexHandler, self).__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data)

        if isinstance(pattern, string_types):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, update):
        if isinstance(update, Update) and update.message and update.message.text:
            match = re.match(self.pattern, update.message.text)
            return bool(match)
        else:
            return False

    def handle_update(self, update, dispatcher):
        optional_args = self.collect_optional_args(dispatcher, update)
        match = re.match(self.pattern, update.message.text)

        if self.pass_groups:
            optional_args['groups'] = match.groups()
        if self.pass_groupdict:
            optional_args['groupdict'] = match.groupdict()

        return self.callback(dispatcher.bot, update, **optional_args)

    # old non-PEP8 Handler methods
    m = "telegram.RegexHandler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
