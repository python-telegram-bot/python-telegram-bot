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

"""
This module contains a object that represents Tests for Updater, Dispatcher,
WebhookServer and WebhookHandler
"""
import logging
import unittest
import sys
import re
import os
import signal
from random import randrange
from time import sleep
from datetime import datetime

try:
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import Request, urlopen

sys.path.append('.')

from telegram import Update, Message, TelegramError, User, Chat, Updater
from telegram.dispatcher import run_async
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


class UpdaterTest(BaseTest, unittest.TestCase):
    """
    This object represents Tests for Updater, Dispatcher, WebhookServer and
    WebhookHandler
    """

    def setUp(self):
        self.updater = Updater('', workers=2)

        self.received_message = None
        self.message_count = 0
        self.lock = Lock()

    def tearDown(self):
        self.updater.stop()

    def reset(self):
        self.message_count = 0
        self.received_message = None

    def telegramHandlerTest(self, bot, update):
        self.received_message = update.message.text
        self.message_count += 1

    @run_async
    def asyncHandlerTest(self, bot, update, **kwargs):
        sleep(1)
        with self.lock:
            self.received_message = update.message.text
            self.message_count += 1

    def stringHandlerTest(self, bot, update):
        self.received_message = update
        self.message_count += 1

    def additionalArgsTest(self, bot, update, update_queue, args):
        self.received_message = update
        self.message_count += 1
        if args[0] == 'resend':
            update_queue.put('/test5 noresend')
        elif args[0] == 'noresend':
            pass

    @run_async
    def asyncAdditionalHandlerTest(self, bot, update, update_queue=None,
                                   **kwargs):
        sleep(1)
        with self.lock:
            if update_queue is not None:
                self.received_message = update.message.text
                self.message_count += 1

    def errorRaisingHandlerTest(self, bot, update):
        raise TelegramError(update)

    def errorHandlerTest(self, bot, update, error):
        self.received_message = error.message
        self.message_count += 1

    def test_addRemoveTelegramMessageHandler(self):
        print('Testing add/removeTelegramMessageHandler')
        bot = MockBot('Test')
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, 'Test')

        # Remove handler
        d.removeTelegramMessageHandler(self.telegramHandlerTest)
        self.reset()

        bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addTelegramMessageHandlerMultipleMessages(self):
        print('Testing addTelegramMessageHandler and send 100 messages...')
        self.updater.bot = MockBot('Multiple', 100)
        self.updater.dispatcher.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.0)
        sleep(2)
        self.assertEqual(self.received_message, 'Multiple')
        self.assertEqual(self.message_count, 100)

    def test_addRemoveTelegramRegexHandler(self):
        print('Testing add/removeStringRegexHandler')
        bot = MockBot('Test2')
        self.updater.bot = bot
        d = self.updater.dispatcher
        regobj = re.compile('Te.*')
        self.updater.dispatcher.addTelegramRegexHandler(regobj,
                                                        self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, 'Test2')

        # Remove handler
        d.removeTelegramRegexHandler(regobj, self.telegramHandlerTest)
        self.reset()

        bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveTelegramCommandHandler(self):
        print('Testing add/removeTelegramCommandHandler')
        bot = MockBot('/test')
        self.updater.bot = bot
        d = self.updater.dispatcher
        self.updater.dispatcher.addTelegramCommandHandler(
            'test', self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, '/test')

        # Remove handler
        d.removeTelegramCommandHandler('test', self.telegramHandlerTest)
        self.reset()

        bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveUnknownTelegramCommandHandler(self):
        print('Testing add/removeUnknownTelegramCommandHandler')
        bot = MockBot('/test2')
        self.updater.bot = bot
        d = self.updater.dispatcher
        self.updater.dispatcher.addUnknownTelegramCommandHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, '/test2')

        # Remove handler
        d.removeUnknownTelegramCommandHandler(self.telegramHandlerTest)
        self.reset()

        bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveStringRegexHandler(self):
        print('Testing add/removeStringRegexHandler')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addStringRegexHandler('Te.*', self.stringHandlerTest)
        queue = self.updater.start_polling(0.01)
        queue.put('Test3')
        sleep(.1)
        self.assertEqual(self.received_message, 'Test3')

        # Remove handler
        d.removeStringRegexHandler('Te.*', self.stringHandlerTest)
        self.reset()

        queue.put('Test3')
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveStringCommandHandler(self):
        print('Testing add/removeStringCommandHandler')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addStringCommandHandler(
            'test3', self.stringHandlerTest)

        queue = self.updater.start_polling(0.01)
        queue.put('/test3')
        sleep(.1)
        self.assertEqual(self.received_message, '/test3')

        # Remove handler
        d.removeStringCommandHandler('test3', self.stringHandlerTest)
        self.reset()

        queue.put('/test3')
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveUnknownStringCommandHandler(self):
        print('Testing add/removeUnknownStringCommandHandler')
        bot = MockBot('/test')
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addUnknownStringCommandHandler(
            self.stringHandlerTest)
        queue = self.updater.start_polling(0.01)
        queue.put('/test4')
        sleep(.1)
        self.assertEqual(self.received_message, '/test4')

        # Remove handler
        d.removeUnknownStringCommandHandler(self.stringHandlerTest)
        self.reset()

        bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveErrorHandler(self):
        print('Testing add/removeErrorHandler')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addErrorHandler(self.errorHandlerTest)
        queue = self.updater.start_polling(0.01)
        error = TelegramError("Unauthorized.")
        queue.put(error)
        sleep(.1)
        self.assertEqual(self.received_message, "Unauthorized.")

        # Remove handler
        d.removeErrorHandler(self.errorHandlerTest)
        self.reset()

        queue.put(error)
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_errorInHandler(self):
        print('Testing error in Handler')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addStringRegexHandler('.*',
                                                self.errorRaisingHandlerTest)
        self.updater.dispatcher.addErrorHandler(self.errorHandlerTest)
        queue = self.updater.start_polling(0.01)

        queue.put('Test Error 1')
        sleep(.1)
        self.assertEqual(self.received_message, 'Test Error 1')

    def test_errorOnGetUpdates(self):
        print('Testing error on getUpdates')
        bot = MockBot('', raise_error=True)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addErrorHandler(self.errorHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, "Test Error 2")

    def test_addRemoveTypeHandler(self):
        print('Testing add/removeTypeHandler')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTypeHandler(dict, self.stringHandlerTest)
        queue = self.updater.start_polling(0.01)
        payload = {"Test": 42}
        queue.put(payload)
        sleep(.1)
        self.assertEqual(self.received_message, payload)

        # Remove handler
        d.removeTypeHandler(dict, self.stringHandlerTest)
        self.reset()

        queue.put(payload)
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_runAsync(self):
        print('Testing @run_async')
        bot = MockBot('Test5', messages=2)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test5')
        self.assertEqual(self.message_count, 2)

    def test_additionalArgs(self):
        print('Testing additional arguments for handlers')
        self.updater.bot = MockBot('', messages=0)
        self.updater.dispatcher.addStringCommandHandler(
            'test5', self.additionalArgsTest)

        queue = self.updater.start_polling(0.01)
        queue.put('/test5 resend')
        sleep(.1)
        self.assertEqual(self.received_message, '/test5 noresend')
        self.assertEqual(self.message_count, 2)

    def test_runAsyncWithAdditionalArgs(self):
        print('Testing @run_async with additional parameters')
        bot = MockBot('Test6', messages=2)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncAdditionalHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test6')
        self.assertEqual(self.message_count, 2)

    def test_webhook(self):
        print('Testing Webhook')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)

        # Select random port for travis
        port = randrange(1024, 49152)
        self.updater.start_webhook('127.0.0.1', port,
                                   url_path='TOKEN',
                                   cert='./tests/test_updater.py',
                                   key='./tests/test_updater.py')
        sleep(0.5)
        # SSL-Wrapping will fail, so we start the server without SSL
        Thread(target=self.updater.httpd.serve_forever).start()

        # Now, we send an update to the server via urlopen
        message = Message(1, User(1, "Tester"), datetime.now(),
                          Chat(1, "group", title="Test Group"))

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

        print("Test other webhook server functionalities...")
        request = Request('http://localhost:%d/webookhandler.py' % port)
        response = urlopen(request)
        self.assertEqual(b'', response.read())
        self.assertEqual(200, response.code)

        request.get_method = lambda: 'HEAD'

        response = urlopen(request)
        self.assertEqual(b'', response.read())
        self.assertEqual(200, response.code)

        # Test multiple shutdown() calls
        self.updater.httpd.shutdown()
        self.updater.httpd.shutdown()
        self.assertTrue(True)

    def test_webhook_no_ssl(self):
        print('Testing Webhook without SSL')
        bot = MockBot('', messages=0)
        self.updater.bot = bot
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)

        # Select random port for travis
        port = randrange(1024, 49152)
        self.updater.start_webhook('127.0.0.1', port)
        sleep(0.5)

        # Now, we send an update to the server via urlopen
        message = Message(1, User(1, "Tester 2"), datetime.now(),
                          Chat(1, 'group', title="Test Group 2"))

        message.text = "Webhook Test 2"
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

        r = Request('http://127.0.0.1:%d/' % port,
                    data=payload,
                    headers=header)

        urlopen(r)
        sleep(1)
        self.assertEqual(self.received_message, 'Webhook Test 2')

    def signalsender(self):
        sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)

    def test_idle(self):
        print('Testing idle')
        self.updater.bot = MockBot('Test6', messages=0)
        self.updater.start_polling(poll_interval=0.01)
        Thread(target=self.signalsender).start()
        self.updater.idle()
        # If we get this far, idle() ran through
        sleep(1)
        self.updater.running = False


class MockBot:

    def __init__(self, text, messages=1, raise_error=False):
        self.text = text
        self.send_messages = messages
        self.raise_error = raise_error
        self.token = "TOKEN"
        pass

    @staticmethod
    def mockUpdate(text):
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
            raise TelegramError('Test Error 2')
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
