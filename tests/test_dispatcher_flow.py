#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
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
This module contains an object that represents Tests for Updater, Dispatcher,
WebhookServer and WebhookHandler
"""
import logging
import sys
import unittest
from queue import Queue

sys.path.append('.')
from telegram import Message, Update, User, Bot
from telegram.ext import CommandHandler, Dispatcher, DispatcherHandlerContinue, \
    DispatcherHandlerStop

from tests.base import BaseTest

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s ' '- %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class DispatcherFlowTest(BaseTest, unittest.TestCase):
    """

    """
    _bot = None
    _update = None

    def setUp(self):
        self._bot = Bot('123:XYZ')
        self._bot.bot = User.de_json(
            {'id': 123, 'first_name': 'TestBot', 'username': 'test_bot'},
            self._bot)
        user = User(id=404, first_name='ihoru')
        # noinspection PyTypeChecker
        message = Message(1, None, None, None, text='/start', bot=self._bot)
        self._update = Update(1, message=message)

    def test_continue_flow(self):
        passed = []

        def start1(b, u):
            passed.append('start1')
            raise DispatcherHandlerContinue

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)

        # Without raising Continue everything should work as before
        passed = []
        dp = Dispatcher(self._bot, Queue())
        dp.add_handler(CommandHandler('start', start3))
        dp.add_handler(CommandHandler('start', start2))
        dp.add_error_handler(error)
        dp.process_update(self._update)
        self.assertEqual(passed, ['start3'])

        # If Continue raised next handler should be proceed.
        passed = []
        dp = Dispatcher(self._bot, Queue())
        dp.add_handler(CommandHandler('start', start1))
        dp.add_handler(CommandHandler('start', start2))
        dp.process_update(self._update)
        self.assertEqual(passed, ['start1', 'start2'])

    def test_stop_flow(self):
        passed = []

        def start1(b, u):
            passed.append('start1')
            raise DispatcherHandlerStop

        def start2(b, u):
            passed.append('start2')

        def start3(b, u):
            passed.append('start3')

        def error(b, u, e):
            passed.append('error')
            passed.append(e)

        # Without raising Stop everything should work as before
        passed = []
        dp = Dispatcher(self._bot, Queue())
        dp.add_handler(CommandHandler('start', start3), 1)
        dp.add_handler(CommandHandler('start', start2), 2)
        dp.add_error_handler(error)
        dp.process_update(self._update)
        self.assertEqual(passed, ['start3', 'start2'])

        # If Stop raised handlers in other groups should not be called.
        passed = []
        dp = Dispatcher(self._bot, Queue())
        dp.add_handler(CommandHandler('start', start1), 1)
        dp.add_handler(CommandHandler('start', start3), 1)
        dp.add_handler(CommandHandler('start', start2), 2)
        dp.process_update(self._update)
        self.assertEqual(passed, ['start1'])


if __name__ == '__main__':
    unittest.main()
