#!/usr/bin/env python
# encoding: utf-8
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

""" This module contains a object that represents Tests for BotEventHandler """

import unittest
import sys
from time import sleep

import re

sys.path.append('.')

from telegram import Update, Message, TelegramError
from tests.base import BaseTest


class BotEventHandlerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Bot."""

    def setUp(self):
        from telegram import BotEventHandler
        self.beh = BotEventHandler('')

        self.received_message = None
        self.message_count = 0

    def tearDown(self):
        self.beh.stop()

    def telegramHandlerTest(self, bot, update):
        self.received_message = update.message.text
        self.message_count += 1

    def stringHandlerTest(self, bot, update):
        self.received_message = update
        self.message_count += 1

    def errorHandlerTest(self, bot, update, error):
        self.received_message = error
        self.message_count += 1

    def test_addTelegramMessageHandler(self):
        print('Testing addTelegramMessageHandler')
        self.beh.bot = MockBot('Test')
        self.beh.broadcaster.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.beh.start_polling(0.05)
        sleep(.1)
        self.assertEqual(self.received_message, 'Test')

    def test_addTelegramMessageHandlerMultipleMessages(self):
        print('Testing addTelegramMessageHandler and send 100 messages...')
        self.beh.bot = MockBot('Multiple', 1000)
        self.beh.broadcaster.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.beh.start_polling(0.0)
        sleep(.1)
        self.assertEqual(self.received_message, 'Multiple')
        self.assertEqual(self.message_count, 1000)

    def test_addTelegramRegexHandler(self):
        print('Testing addStringRegexHandler')
        self.beh.bot = MockBot('Test2')
        self.beh.broadcaster.addTelegramRegexHandler(re.compile('Te.*'),
                                                   self.telegramHandlerTest)
        self.beh.start_polling(0.05)
        sleep(.1)
        self.assertEqual(self.received_message, 'Test2')

    def test_addTelegramCommandHandler(self):
        print('Testing addTelegramCommandHandler')
        self.beh.bot = MockBot('/test')
        self.beh.broadcaster.addTelegramCommandHandler(
            'test', self.telegramHandlerTest)
        self.beh.start_polling(0.05)
        sleep(.1)
        self.assertEqual(self.received_message, '/test')

    def test_addUnknownTelegramCommandHandler(self):
        print('Testing addUnknownTelegramCommandHandler')
        self.beh.bot = MockBot('/test2')
        self.beh.broadcaster.addUnknownTelegramCommandHandler(
            self.telegramHandlerTest)
        self.beh.start_polling(0.05)
        sleep(.1)
        self.assertEqual(self.received_message, '/test2')

    def test_addStringRegexHandler(self):
        print('Testing addStringRegexHandler')
        self.beh.bot = MockBot('')
        self.beh.broadcaster.addStringRegexHandler(re.compile('Te.*'),
                                                   self.stringHandlerTest)
        queue = self.beh.start_polling(0.05)
        queue.put('Test3')
        sleep(.1)
        self.assertEqual(self.received_message, 'Test3')

    def test_addStringCommandHandler(self):
        print('Testing addStringCommandHandler')
        self.beh.bot = MockBot('')
        self.beh.broadcaster.addStringCommandHandler(
            'test3', self.stringHandlerTest)

        queue = self.beh.start_polling(0.05)
        queue.put('/test3')
        sleep(.1)
        self.assertEqual(self.received_message, '/test3')

    def test_addUnknownStringCommandHandler(self):
        print('Testing addUnknownStringCommandHandler')
        self.beh.bot = MockBot('/test')
        self.beh.broadcaster.addUnknownStringCommandHandler(
            self.stringHandlerTest)
        queue = self.beh.start_polling(0.05)
        queue.put('/test4')
        sleep(.1)
        self.assertEqual(self.received_message, '/test4')

    def test_addErrorHandler(self):
        print('Testing addErrorHandler')
        self.beh.bot = MockBot('')
        self.beh.broadcaster.addErrorHandler(self.errorHandlerTest)
        queue = self.beh.start_polling(0.05)
        error = TelegramError("Unauthorized.")
        queue.put(error)
        sleep(.1)
        self.assertEqual(self.received_message, error)

    def test_addTypeHandler(self):
        print('Testing addTypeHandler')
        self.beh.bot = MockBot('')
        self.beh.broadcaster.addTypeHandler(dict, self.stringHandlerTest)
        queue = self.beh.start_polling(0.05)
        payload = {"Test": 42}
        queue.put(payload)
        sleep(.1)
        self.assertEqual(self.received_message, payload)

class MockBot:

    def __init__(self, text, messages=1):
        self.text = text
        self.send_messages = messages
        pass

    def mockUpdate(self, text):
        message = Message(0, None, None, None)
        message.text = text
        update = Update(0)
        update.message = message
        return update

    def setWebhook(self, webhook_url=None, certificate=None):
        pass

    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0,
                   network_delay=2.):

        if self.send_messages >= 2:
            self.send_messages -= 2
            return self.mockUpdate(self.text), self.mockUpdate(self.text)
        elif self.send_messages == 1:
            self.send_messages -= 1
            return self.mockUpdate(self.text),
        else:
            return []

if __name__ == '__main__':
    unittest.main()
