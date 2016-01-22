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

"""This module contains the class UpdateQueue to override standard
Queue."""


# Adjust for differences in Python versions
try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class UpdateQueue(Queue):
    """
    This class overrides standard Queues. Allows you to de/queue context
    data apart from the handled `update`
    """

    def put(self, item, block=True, timeout=None, context=None):
        """
        Put an item into the queue with context data if provided as a
        tuple (item, context). Overrides standard Queue.put method.

        Args:
            update (any): handled by the dispatcher
            context (any): extra data to use in handlers
        """
        Queue.put(self, (item, context), block, timeout)

    def get(self, block=True, timeout=None, context=False):
        """
        Remove and return an item from the queue. A tuple of
        (update, context) if requested. Overrides standard Queue.get
        method.

        Args:
            context (boolean): set true to get (update, context)
                
        """
        if not context:
            return Queue.get(self, block, timeout)[0]
        return Queue.get(self, block, timeout)
