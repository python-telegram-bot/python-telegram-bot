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

    Args:
        pattern (:obj:`str` | :obj:`Pattern`): The regex pattern.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.

    """

    def __init__(self, pattern, callback):
        super(StringRegexHandler, self).__init__(callback)

        if isinstance(pattern, string_types):
            pattern = re.compile(pattern)

        self.pattern = pattern

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`str`): An incoming command.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, string_types):
            match = re.match(self.pattern, update)
            if match:
                return match

    def collect_additional_context(self, context, update, dispatcher, check_result):
        if self.pattern:
            context.matches = [check_result]
