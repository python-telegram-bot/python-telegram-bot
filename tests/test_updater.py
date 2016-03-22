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
from future.builtins import bytes

if sys.version_info[0:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

try:
    # python2
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    # python3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

sys.path.append('.')

from telegram import Update, Message, TelegramError, User, Chat, Bot
from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
from telegram.error import Unauthorized, InvalidToken
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

    def test_importLegacyUpdater(self):
        from telegram import Updater as legacyUpdater

        lu = legacyUpdater(workers=2, bot=Bot('123:abcd'))

        self.assertIsInstance(lu, Updater)

        lu.stop()

    def test_importLegacyDispatcher(self):
        from telegram.ext import Dispatcher
        from telegram.utils.updatequeue import UpdateQueue
        from telegram import Dispatcher as legacyDispatcher

        lp = legacyDispatcher(bot=Bot('123:abcd'), update_queue=UpdateQueue())

        self.assertIsInstance(lp, Dispatcher)

        lp.stop()

    def test_addRemoveTelegramMessageHandler(self):
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
        self._setup_updater('Multiple', 100)
        self.updater.dispatcher.addTelegramMessageHandler(
            self.telegramHandlerTest)
        self.updater.start_polling(0.0)
        sleep(2)
        self.assertEqual(self.received_message, 'Multiple')
        self.assertEqual(self.message_count, 100)

    def test_addRemoveTelegramRegexHandler(self):
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
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addStringRegexHandler('.*', self.errorRaisingHandlerTest)
        self.updater.dispatcher.addErrorHandler(self.errorHandlerTest)
        queue = self.updater.start_polling(0.01)

        queue.put('Test Error 1')
        sleep(.1)
        self.assertEqual(self.received_message, 'Test Error 1')

    def test_cleanBeforeStart(self):
        self._setup_updater('')
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(self.telegramHandlerTest)
        self.updater.start_polling(0.01, clean=True)
        sleep(.1)
        self.assertEqual(self.message_count, 0)
        self.assertIsNone(self.received_message)

    def test_errorOnGetUpdates(self):
        self._setup_updater('', raise_error=True)
        d = self.updater.dispatcher
        d.addErrorHandler(self.errorHandlerTest)
        self.updater.start_polling(0.01)
        sleep(.1)
        self.assertEqual(self.received_message, "Test Error 2")

    def test_addRemoveTypeHandler(self):
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
        self._setup_updater('Test5', messages=2)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test5')
        self.assertEqual(self.message_count, 2)

    def test_additionalArgs(self):
        self._setup_updater('', messages=0)
        self.updater.dispatcher.addStringCommandHandler(
            'test5', self.additionalArgsTest)

        queue = self.updater.start_polling(0.01)
        queue.put('/test5 resend')
        sleep(.1)
        self.assertEqual(self.received_message, '/test5 noresend')
        self.assertEqual(self.message_count, 2)
        
    def test_context(self):
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
        self._setup_updater('Test6', messages=2)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.asyncAdditionalHandlerTest)
        self.updater.start_polling(0.01)
        sleep(1.2)
        self.assertEqual(self.received_message, 'Test6')
        self.assertEqual(self.message_count, 2)

    def test_webhook(self):
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port for travis
        self.updater.start_webhook(ip, port,
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

        self._send_webhook_msg(ip, port, update.to_json(), 'TOKEN')

        sleep(1)
        self.assertEqual(self.received_message, 'Webhook Test')

        print("Test other webhook server functionalities...")
        response = self._send_webhook_msg(ip, port, None, 'webookhandler.py')
        self.assertEqual(b'', response.read())
        self.assertEqual(200, response.code)

        response = self._send_webhook_msg(ip, port, None, 'webookhandler.py',
                                          get_method=lambda: 'HEAD')

        self.assertEqual(b'', response.read())
        self.assertEqual(200, response.code)

        # Test multiple shutdown() calls
        self.updater.httpd.shutdown()
        self.updater.httpd.shutdown()
        self.assertTrue(True)

    def test_webhook_no_ssl(self):
        self._setup_updater('', messages=0)
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(
            self.telegramHandlerTest)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port for travis
        self.updater.start_webhook(ip, port)
        sleep(0.5)

        # Now, we send an update to the server via urlopen
        message = Message(1, User(1, "Tester 2"), datetime.now(),
                          Chat(1, 'group', title="Test Group 2"))

        message.text = "Webhook Test 2"
        update = Update(1)
        update.message = message

        self._send_webhook_msg(ip, port, update.to_json())
        sleep(1)
        self.assertEqual(self.received_message, 'Webhook Test 2')

    def test_bootstrap_retries_success(self):
        retries = 3
        self._setup_updater('', messages=0, bootstrap_retries=retries)

        self.updater._set_webhook('path', retries)
        self.assertEqual(self.updater.bot.bootstrap_attempts, retries)

    def test_bootstrap_retries_unauth(self):
        retries = 3
        self._setup_updater('', messages=0, bootstrap_retries=retries,
                            bootstrap_err=Unauthorized())

        self.assertRaises(Unauthorized, self.updater._set_webhook, 'path',
                          retries)
        self.assertEqual(self.updater.bot.bootstrap_attempts, 1)

    def test_bootstrap_retries_invalid_token(self):
        retries = 3
        self._setup_updater('', messages=0, bootstrap_retries=retries,
                            bootstrap_err=InvalidToken())

        self.assertRaises(InvalidToken, self.updater._set_webhook, 'path',
                          retries)
        self.assertEqual(self.updater.bot.bootstrap_attempts, 1)

    def test_bootstrap_retries_fail(self):
        retries = 1
        self._setup_updater('', messages=0, bootstrap_retries=retries)

        self.assertRaisesRegexp(TelegramError, 'test',
                                self.updater._set_webhook, 'path', retries - 1)
        self.assertEqual(self.updater.bot.bootstrap_attempts, 1)

    def test_webhook_invalid_posts(self):
        self._setup_updater('', messages=0)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # select random port for travis
        thr = Thread(target=self.updater._start_webhook,
                     args=(ip, port, '', None, None, 0, None))
        thr.start()

        sleep(0.5)

        try:
            with self.assertRaises(HTTPError) as ctx:
                self._send_webhook_msg(ip, port,
                                       '<root><bla>data</bla></root>',
                                       content_type='application/xml')
            self.assertEqual(ctx.exception.code, 403)

            with self.assertRaises(HTTPError) as ctx:
                self._send_webhook_msg(ip, port, 'dummy-payload',
                                       content_len=-2)
            self.assertEqual(ctx.exception.code, 403)

            # TODO: prevent urllib or the underlying from adding content-length
            # with self.assertRaises(HTTPError) as ctx:
            #     self._send_webhook_msg(ip, port, 'dummy-payload',
            #                            content_len=None)
            # self.assertEqual(ctx.exception.code, 411)

            with self.assertRaises(HTTPError) as ctx:
                self._send_webhook_msg(ip, port, 'dummy-payload',
                                       content_len='not-a-number')
            self.assertEqual(ctx.exception.code, 403)

        finally:
            self.updater._stop_httpd()
            thr.join()

    def _send_webhook_msg(self, ip, port, payload_str, url_path='',
                          content_len=-1, content_type='application/json',
                          get_method=None):
        headers = {
            'content-type': content_type,
        }

        if not payload_str:
            content_len = None
            payload = None
        else:
            payload = bytes(payload_str, encoding='utf-8')

        if content_len == -1:
            content_len = len(payload)

        if content_len is not None:
            headers['content-length'] = str(content_len)

        url = 'http://{ip}:{port}/{path}'.format(ip=ip, port=port,
                                                 path=url_path)

        req = Request(url, data=payload, headers=headers)


        if get_method is not None:
            req.get_method = get_method

        return urlopen(req)

    def signalsender(self):
        sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)

    def test_idle(self):
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

    def __init__(self, text, messages=1, raise_error=False,
                 bootstrap_retries=None, bootstrap_err=TelegramError('test')):
        self.text = text
        self.send_messages = messages
        self.raise_error = raise_error
        self.token = "TOKEN"
        self.bootstrap_retries = bootstrap_retries
        self.bootstrap_attempts = 0
        self.bootstrap_err = bootstrap_err

    @staticmethod
    def mockUpdate(text):
        message = Message(0, None, None, None)
        message.text = text
        update = Update(0)
        update.message = message
        return update

    def setWebhook(self, webhook_url=None, certificate=None):
        if self.bootstrap_retries is None:
            return

        if self.bootstrap_attempts < self.bootstrap_retries:
            self.bootstrap_attempts += 1
            raise self.bootstrap_err

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
