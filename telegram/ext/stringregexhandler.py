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

""" This module contains the base class for handlers as used by the
Dispatcher """

import re

from .handler import Handler


class RegexHandler(Handler):
    """
    Handler class to handle string updates based on a regex. It uses a
    regular expression to check update content. Read the documentation of the
    ``re`` module for more information. The ``re.match`` function is used to
    determine if an update should be handled by this handler.

    Args:
        pattern (str or Pattern): The regex pattern.
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``checkUpdate``
            has determined that an update should be processed by this handler.
        pass_groups (optional[bool]): If the callback should be passed the
            result of ``re.match(pattern, update).groups()`` as a keyword
            argument called ``groups``. Default is ``False``
        pass_groupdict (optional[bool]): If the callback should be passed the
            result of ``re.match(pattern, update).groupdict()`` as a keyword
            argument called ``groupdict``. Default is ``False``
        pass_update_queue (optional[bool]): If the handler should be passed the
            update queue as a keyword argument called ``update_queue``. It can
            be used to insert updates. Default is ``False``
    """

    def __init__(self, pattern, callback, pass_groups=False,
                 pass_groupdict=False, pass_update_queue=False):
        super(Handler).__init__(callback, pass_update_queue)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def checkUpdate(self, update):
        if isinstance(update, str):
            match = re.match(self.pattern, update)
            return bool(match)
        else:
            return False

    def handleUpdate(self, update, dispatcher):
        optional_args = self.collectOptionalArgs(dispatcher)
        match = re.match(self.pattern, update)

        if self.pass_groups:
            optional_args['groups'] = match.groups()
        if self.pass_groupdict:
            optional_args['groupdict'] = match.groupdict()

        self.callback(dispatcher.bot, update, **optional_args)
