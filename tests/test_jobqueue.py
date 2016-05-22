#!/usr/bin/env python
# encoding: utf-8
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
"""
This module contains a object that represents Tests for JobQueue
"""
import logging
import sys
from time import sleep

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

sys.path.append('.')

from telegram.ext import JobQueue, Updater
from tests.base import BaseTest

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class JobQueueTest(BaseTest, unittest.TestCase):
    """
    This object represents Tests for Updater, Dispatcher, WebhookServer and
    WebhookHandler
    """

    def setUp(self):
        self.jq = JobQueue("Bot", tick_interval=0.005)
        self.result = 0

    def tearDown(self):
        if self.jq is not None:
            self.jq.stop()

    def job1(self, bot):
        self.result += 1

    def job2(self, bot):
        raise Exception("Test Error")

    def test_basic(self):
        self.jq.put(self.job1, 0.1)
        sleep(1.5)
        self.assertGreaterEqual(self.result, 10)

    def test_noRepeat(self):
        self.jq.put(self.job1, 0.1, repeat=False)
        sleep(0.5)
        self.assertEqual(1, self.result)

    def test_nextT(self):
        self.jq.put(self.job1, 0.1, next_t=0.5)
        sleep(0.45)
        self.assertEqual(0, self.result)
        sleep(0.1)
        self.assertEqual(1, self.result)

    def test_multiple(self):
        self.jq.put(self.job1, 0.1, repeat=False)
        self.jq.put(self.job1, 0.2, repeat=False)
        self.jq.put(self.job1, 0.4)
        sleep(1)
        self.assertEqual(4, self.result)

    def test_error(self):
        self.jq.put(self.job2, 0.1)
        self.jq.put(self.job1, 0.2)
        self.jq.start()
        sleep(0.4)
        self.assertEqual(1, self.result)

    def test_inUpdater(self):
        u = Updater(bot="MockBot", job_queue_tick_interval=0.005)
        u.job_queue.put(self.job1, 0.5)
        sleep(0.75)
        self.assertEqual(1, self.result)
        u.stop()
        sleep(2)
        self.assertEqual(1, self.result)


if __name__ == '__main__':
    unittest.main()
