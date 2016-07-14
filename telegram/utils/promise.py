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
""" This module contains the Promise class """

from threading import Event


class Promise(object):
    """A simple Promise implementation for the run_async decorator"""

    def __init__(self, pooled_function, args, kwargs):
        self.pooled_function = pooled_function
        self.args = args
        self.kwargs = kwargs
        self.done = Event()
        self._result = None

    def run(self):
        try:
            self._result = self.pooled_function(*self.args, **self.kwargs)

        except:
            raise

        finally:
            self.done.set()

    def result(self, timeout=None):
        self.done.wait(timeout=timeout)
        return self._result
