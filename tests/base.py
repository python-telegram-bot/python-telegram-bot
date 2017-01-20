#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains an object that represents a Base class for tests"""

import os
import signal
import sys

from nose.tools import make_decorator

sys.path.append('.')

import json
import telegram


class BaseTest(object):
    """This object represents a Base test and its sets of functions."""

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)

        bot = telegram.Bot(
            os.environ.get('TOKEN', '133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0'))
        chat_id = os.environ.get('CHAT_ID', '12173560')

        self._group_id = os.environ.get('GROUP_ID', '-49740850')
        self._channel_id = os.environ.get('CHANNEL_ID', '@pythontelegrambottests')
        self._bot = bot
        self._chat_id = chat_id

    @staticmethod
    def is_json(string):
        try:
            json.loads(string)
        except ValueError:
            return False

        return True

    @staticmethod
    def is_dict(dictionary):
        if isinstance(dictionary, dict):
            return True

        return False


class TestTimedOut(AssertionError):

    def __init__(self, time_limit, frame):
        super(TestTimedOut, self).__init__('time_limit={0}'.format(time_limit))
        self.time_limit = time_limit
        self.frame = frame


def timeout(time_limit):

    def decorator(func):

        def timed_out(_signum, frame):
            raise TestTimedOut(time_limit, frame)

        def newfunc(*args, **kwargs):
            try:
                # Will only work on unix systems
                orig_handler = signal.signal(signal.SIGALRM, timed_out)
                signal.alarm(time_limit)
            except AttributeError:
                pass
            try:
                rc = func(*args, **kwargs)
            finally:
                try:
                    # Will only work on unix systems
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, orig_handler)
                except AttributeError:
                    pass
            return rc

        newfunc = make_decorator(func)(newfunc)
        return newfunc

    return decorator
