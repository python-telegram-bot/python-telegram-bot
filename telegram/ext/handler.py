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

from telegram.utils.deprecate import deprecate


class Handler(object):
    """
    The base class for all update handlers. You can create your own handlers
    by inheriting from this class.

    Args:
        callback (function): A function that takes ``bot, update`` as
            positional arguments. It will be called when the ``check_update``
            has determined that an update should be processed by this handler.
        pass_update_queue (optional[bool]): If the callback should be passed
            the update queue as a keyword argument called ``update_queue``. It
            can be used to insert updates. Default is ``False``
    """

    def __init__(self, callback, pass_update_queue=False):
        self.callback = callback
        self.pass_update_queue = pass_update_queue

    def check_update(self, update):
        """
        This method is called to determine if an update should be handled by
        this handler instance. It should always be overridden.

        Args:
            update (object): The update to be tested

        Returns:
            bool
        """
        raise NotImplementedError

    def handle_update(self, update, dispatcher):
        """
        This method is called if it was determined that an update should indeed
        be handled by this instance. It should also be overridden, but in most
        cases call self.callback(dispatcher.bot, update), possibly along with
        optional arguments.

        Args:
            update (object): The update to be handled

        """
        raise NotImplementedError

    def collect_optional_args(self, dispatcher):
        """
        Prepares the optional arguments that are the same for all types of
        handlers

        Args:
            dispatcher (Dispatcher):
        """
        optional_args = dict()
        if self.pass_update_queue:
            optional_args['update_queue'] = dispatcher.update_queue

        return optional_args

    # old non-PEP8 Handler methods
    m = "telegram.Handler."
    checkUpdate = deprecate(check_update, m + "checkUpdate", m + "check_update")
    handleUpdate = deprecate(handle_update, m + "handleUpdate", m + "handle_update")
    collectOptionalArgs = deprecate(collect_optional_args, m + "collectOptionalArgs",
                                    m + "collect_optional_args")
