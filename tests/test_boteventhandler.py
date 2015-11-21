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
import logging
import unittest
import sys
import re
from random import randrange
from time import sleep
from datetime import datetime

try:
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import Request, urlopen

sys.path.append('.')

from telegram import Update, Message, TelegramError, User, GroupChat
from telegram.broadcaster import run_async
from tests.base import BaseTest
from threading import Lock, Thread

# Enable logging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class BotEventHandlerTest(BaseTest, unittest.TestCase):
    """This object represents Tests for Telegram Bot."""

    def setUp(self):
        from telegram import BotEventHandler
        self.beh = BotEventHandler('', workers=2)

        self.received_message = None
        self.message_count = 0
        self.lock = Lock()

    def tearDown(self):
        self.beh.stop()

    def telegramHandlerTest(self, bot, update):
        self.received_message = update.message.text
        self.message_count += 1

    @run_async
    def asyncHandlerTest(self, bot, update):
        sleep(1)
        with self.lock:
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
        self.beh.bot = MockBot('Multiple', 100)
        self.beh.broadcaster.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.beh.start_polling(0.0)
        sleep(.5)
        self.assertEqual(self.received_message, 'Multiple')
        self.assertEqual(self.message_count, 100)

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

    def test_errorOnGetUpdates(self):
        print('Testing errorOnGetUpdates')
        self.beh.bot = MockBot('', raise_error=True)
        self.beh.broadcaster.addErrorHandler(self.errorHandlerTest)
        self.beh.start_polling(0.05)
        sleep(.1)
        self.assertEqual(self.received_message.message, "Test Error")

    def test_addTypeHandler(self):
        print('Testing addTypeHandler')
        self.beh.bot = MockBot('')
        self.beh.broadcaster.addTypeHandler(dict, self.stringHandlerTest)
        queue = self.beh.start_polling(0.05)
        payload = {"Test": 42}
        queue.put(payload)
        sleep(.1)
        self.assertEqual(self.received_message, payload)

    def test_runAsync(self):
        print('Testing @run_async')
        self.beh.bot = MockBot('Test4', messages=2)
        self.beh.broadcaster.addTelegramMessageHandler(
            self.asyncHandlerTest)
        self.beh.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test4')
        self.assertEqual(self.message_count, 2)

    def test_webhook(self):
        print('Testing Webhook')
        self.beh.bot = MockBot('Test4', messages=2)
        self.beh.broadcaster.addTelegramMessageHandler(
            self.telegramHandlerTest)

        # Select random port for travis
        port = randrange(1024, 49152)
        self.beh.start_webhook('127.0.0.1', port,
                               './tests/test_boteventhandler.py',
                               './tests/test_boteventhandler.py',
                               listen='127.0.0.1')
        sleep(0.5)
        # SSL-Wrapping will fail, so we start the server without SSL
        Thread(target=self.beh.httpd.serve_forever).start()

        # Now, we send an update to the server via urlopen
        message = Message(1, User(1, "Tester"), datetime.now(),
                          GroupChat(1, "Test Group"))

        message.text = "Webhook Test"
        update = Update(1)
        update.message = message

        try:
            payload = bytes(update.to_json(), encoding='utf-8')
        except TypeError:
            payload = bytes(update.to_json())

        header = {
            'content-type': 'application/json',
            'content-length': str(len(payload))
        }

        r = Request('http://127.0.0.1:%d/TOKEN' % port,
                    data=payload,
                    headers=header)

        urlopen(r)

        sleep(1)
        self.assertEqual(self.received_message, 'Webhook Test')


class MockBot:

    def __init__(self, text, messages=1, raise_error=False):
        self.text = text
        self.send_messages = messages
        self.raise_error = raise_error
        self.token = "TOKEN"
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

        if self.raise_error:
            raise TelegramError('Test Error')
        elif self.send_messages >= 2:
            self.send_messages -= 2
            return self.mockUpdate(self.text), self.mockUpdate(self.text)
        elif self.send_messages == 1:
            self.send_messages -= 1
            return self.mockUpdate(self.text),
        else:
            return []

if __name__ == '__main__':
    unittest.main()
