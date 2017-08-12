#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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

from future.utils import string_types

from .handler import Handler


class StringRegexHandler(Handler):
    """Handler class to handle string updates based on a regex which checks the update content.

    Read the documentation of the ``re`` module for more information. The ``re.match`` function is
    used to determine if an update should be handled by this handler.

    Note:
        This handler is not used to handle Telegram :attr:`telegram.Update`, but strings manually
        put in the queue. For example to send messages with the bot using command line or API.

    Attributes:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler.
        pass_groups (:obj:`bool`): Optional. Determines whether ``groups`` will be passed to the
            callback function.
        pass_groupdict (:obj:`bool`): Optional. Determines whether ``groupdict``. will be passed to
            the callback function.
        pass_update_queue (:obj:`bool`): Optional. Determines whether ``update_queue`` will be
            passed to the callback function.
        pass_job_queue (:obj:`bool`): Optional. Determines whether ``job_queue`` will be passed to
            the callback function.

    Args:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): A function that takes ``bot, update`` as positional arguments.
            It will be called when the :attr:`check_update` has determined that an update should be
            processed by this handler.
        pass_groups (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groups()`` as a keyword argument called ``groups``.
            Default is ``False``
        pass_groupdict (:obj:`bool`, optional): If the callback should be passed the result of
            ``re.match(pattern, data).groupdict()`` as a keyword argument called ``groupdict``.
            Default is ``False``
        pass_update_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``update_queue`` will be passed to the callback function. It will be the ``Queue``
            instance used by the :class:`telegram.ext.Updater` and :class:`telegram.ext.Dispatcher`
            that contains new updates which can be used to insert updates. Default is ``False``.
        pass_job_queue (:obj:`bool`, optional): If set to ``True``, a keyword argument called
            ``job_queue`` will be passed to the callback function. It will be a
            :class:`telegram.ext.JobQueue` instance created by the :class:`telegram.ext.Updater`
            which can be used to schedule new jobs. Default is ``False``.

    """

    def __init__(self,
                 pattern,
                 callback,
                 pass_groups=False,
                 pass_groupdict=False,
                 pass_update_queue=False,
                 pass_job_queue=False):
        super(StringRegexHandler, self).__init__(
            callback, pass_update_queue=pass_update_queue, pass_job_queue=pass_job_queue)

        if isinstance(pattern, string_types):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`str`): An incomming command.

        Returns:
            :obj:`bool`

        """
        return isinstance(update, string_types) and bool(re.match(self.pattern, update))

    def handle_update(self, update, dispatcher):
        """Send the update to the :attr:`callback`.

        Args:
            update (:obj:`str`): An incomming command.
            dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that originated the command.

        """
        optional_args = self.collect_optional_args(dispatcher)
        match = re.match(self.pattern, update)

        if self.pass_groups:
            optional_args['groups'] = match.groups()
        if self.pass_groupdict:
            optional_args['groupdict'] = match.groupdict()

        return self.callback(dispatcher.bot, update, **optional_args)
