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
This module contains a object that represents Tests for Updater, Dispatcher,
WebhookServer and WebhookHandler
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

from telegram import Update, Message, TelegramError, User, Chat, Updater, Bot
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
        self.updater = None
        self.received_message = None
        self.message_count = 0
        self.lock = Lock()

    def _setup_updater(self, *args, **kwargs):
        bot = MockBot(*args, **kwargs)
        self.updater = Updater(workers=2, bot=bot)

    def tearDown(self):
        if self.updater is not None:
            self.updater.stop()

    def reset(self):
        self.message_count = 0
        self.received_message = None

    def telegramHandlerTest(self, bot, update):
        self.received_message = update.message.text
        self.message_count += 1

    def telegramInlineHandlerTest(self, bot, update):
        self.received_message = (update.inline_query,
                                 update.chosen_inline_result)
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

    def regexGroupHandlerTest(self, bot, update, groups=None, groupdict=None):
        self.received_message = (groups, groupdict)
        self.message_count += 1

    def additionalArgsTest(self, bot, update, update_queue, args):
        self.received_message = update
        self.message_count += 1
        if args[0] == 'resend':
            update_queue.put('/test5 noresend')
        elif args[0] == 'noresend':
            pass
        
    def contextTest(self, bot, update, context):
        self.received_message = update
        self.message_count += 1
        self.context = context

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
        self._setup_updater('Test')
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, 'Test')

        # Remove handler
        d.removeTelegramMessageHandler(self.telegramHandlerTest)
        self.reset()

        self.updater.bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addTelegramMessageHandlerMultipleMessages(self):
        print('Testing addTelegramMessageHandler and send 100 messages...')
        self._setup_updater('Multiple', 100)
        self.updater.dispatcher.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.0)
        sleep(2)
        self.assertEqual(self.received_message, 'Multiple')
        self.assertEqual(self.message_count, 100)

    def test_addRemoveTelegramRegexHandler(self):
        print('Testing add/removeStringRegexHandler')
        self._setup_updater('Test2')
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

        self.updater.bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveTelegramCommandHandler(self):
        print('Testing add/removeTelegramCommandHandler')
        self._setup_updater('/test')
        d = self.updater.dispatcher
        self.updater.dispatcher.addTelegramCommandHandler(
            'test', self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, '/test')

        # Remove handler
        d.removeTelegramCommandHandler('test', self.telegramHandlerTest)
        self.reset()

        self.updater.bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveUnknownTelegramCommandHandler(self):
        print('Testing add/removeUnknownTelegramCommandHandler')
        self._setup_updater('/test2')
        d = self.updater.dispatcher
        self.updater.dispatcher.addUnknownTelegramCommandHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, '/test2')

        # Remove handler
        d.removeUnknownTelegramCommandHandler(self.telegramHandlerTest)
        self.reset()

        self.updater.bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveStringRegexHandler(self):
        print('Testing add/removeStringRegexHandler')
        self._setup_updater('', messages=0)
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
        self._setup_updater('', messages=0)
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
        self._setup_updater('/test')
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

        self.updater.bot.send_messages = 1
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_addRemoveErrorHandler(self):
        print('Testing add/removeErrorHandler')
        self._setup_updater('', messages=0)
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
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addStringRegexHandler('.*', self.errorRaisingHandlerTest)
        self.updater.dispatcher.addErrorHandler(self.errorHandlerTest)
        queue = self.updater.start_polling(0.01)

        queue.put('Test Error 1')
        sleep(.1)
        self.assertEqual(self.received_message, 'Test Error 1')

    def test_errorOnGetUpdates(self):
        print('Testing error on getUpdates')
        self._setup_updater('', raise_error=True)
        d = self.updater.dispatcher
        d.addErrorHandler(self.errorHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, "Test Error 2")

    def test_addRemoveTypeHandler(self):
        print('Testing add/removeTypeHandler')
        self._setup_updater('', messages=0)
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

    def test_addRemoveInlineHandlerQuery(self):
        print('Testing add/removeInlineHandler')
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addTelegramInlineHandler(self.telegramInlineHandlerTest)
        queue = self.updater.start_polling(0.01)
        update = Update(update_id=0, inline_query="testquery")
        update2 = Update(update_id=0, chosen_inline_result="testresult")
        queue.put(update)
        sleep(.1)
        self.assertEqual(self.received_message[0], "testquery")

        queue.put(update2)
        sleep(.1)
        self.assertEqual(self.received_message[1], "testresult")

        # Remove handler
        d.removeTelegramInlineHandler(self.telegramInlineHandlerTest)
        self.reset()

        queue.put(update)
        sleep(.1)
        self.assertTrue(None is self.received_message)

    def test_runAsync(self):
        print('Testing @run_async')
        self._setup_updater('Test5', messages=2)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test5')
        self.assertEqual(self.message_count, 2)

    def test_additionalArgs(self):
        print('Testing additional arguments for handlers')
        self._setup_updater('', messages=0)
        self.updater.dispatcher.addStringCommandHandler(
            'test5', self.additionalArgsTest)

        queue = self.updater.start_polling(0.01)
        queue.put('/test5 resend')
        sleep(.1)
        self.assertEqual(self.received_message, '/test5 noresend')
        self.assertEqual(self.message_count, 2)
        
    def test_context(self):
        print('Testing context for handlers')
        context = "context_data"
        self._setup_updater('', messages=0)
        self.updater.dispatcher.addStringCommandHandler(
            'test_context', self.contextTest)
        
        queue = self.updater.start_polling(0.01)
        queue.put('/test_context', context=context)
        sleep(.5)
        self.assertEqual(self.received_message, '/test_context')
        self.assertEqual(self.message_count, 1)
        self.assertEqual(self.context, context)

    def test_regexGroupHandler(self):
        print('Testing optional groups and groupdict parameters')
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addStringRegexHandler('^(This).*?(?P<testgroup>regex group).*',
                                self.regexGroupHandlerTest)
        queue = self.updater.start_polling(0.01)
        queue.put('This is a test message for regex group matching.')
        sleep(.1)
        self.assertEqual(self.received_message, (('This', 'regex group'),
                                                 {'testgroup': 'regex group'}))


    def test_runAsyncWithAdditionalArgs(self):
        print('Testing @run_async with additional parameters')
        self._setup_updater('Test6', messages=2)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncAdditionalHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test6')
        self.assertEqual(self.message_count, 2)

    def test_webhook(self):
        print('Testing Webhook')
        self._setup_updater('', messages=0)
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
        self._setup_updater('', messages=0)
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
        self._setup_updater('Test6', messages=0)
        self.updater.start_polling(poll_interval=0.01)
        Thread(target=self.signalsender).start()
        self.updater.idle()
        # If we get this far, idle() ran through
        sleep(1)
        self.assertFalse(self.updater.running)

    def test_createBot(self):
        updater = Updater('123:abcd')
        self.assertIsNotNone(updater.bot)

    def test_mutualExclusiveTokenBot(self):
        bot = Bot('123:zyxw')
        self.assertRaises(ValueError, Updater, token='123:abcd', bot=bot)

    def test_noTokenOrBot(self):
        self.assertRaises(ValueError, Updater)


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
