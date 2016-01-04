#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <devs@python-telegram-bot.org>
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

"""
This module contains a object that represents Tests for JobQueue
"""
import logging
import sys
import re
import os
import signal
from random import randrange
from time import sleep
from datetime import datetime

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

try:
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import Request, urlopen

sys.path.append('.')

from telegram import JobQueue
from tests.base import BaseTest

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class UpdaterTest(BaseTest, unittest.TestCase):
    """
    This object represents Tests for Updater, Dispatcher, WebhookServer and
    WebhookHandler
    """

    def setUp(self):
        self.jq = JobQueue("Bot", tick_interval=0.001)
        self.result = 0

    def tearDown(self):
        if self.jq is not None:
            self.jq.stop()

    def job1(self, bot):
        self.result += 1

    def test_basic(self):
        print('Testing basic job queue function')
        self.jq.put(self.job1, 0.1)
        self.jq.start()
        sleep(1.05)
        self.assertEqual(10, self.result)

    def test_noRepeat(self):
        print('Testing job queue without repeat')
        self.jq.put(self.job1, 0.1, repeat=False)
        self.jq.start()
        sleep(0.5)
        self.assertEqual(1, self.result)

    def test_nextT(self):
        print('Testing job queue with a set next_t value')
        self.jq.put(self.job1, 0.1, next_t=0.5)
        self.jq.start()
        sleep(0.45)
        self.assertEqual(0, self.result)
        sleep(0.1)
        self.assertEqual(1, self.result)

if __name__ == '__main__':
    unittest.main()
