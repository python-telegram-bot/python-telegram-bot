#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
import logging
import os
import signal
import sys
from functools import partial
from queue import Queue
from random import randrange
from threading import Thread, Event
from time import sleep

try:
    # python2
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    # python3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

import pytest
from future.builtins import bytes

from telegram import TelegramError, Message, User, Chat, Update, Bot
from telegram.error import Unauthorized, InvalidToken, TimedOut, RetryAfter
from telegram.ext import Updater

signalskip = pytest.mark.skipif(sys.platform == 'win32',
                                reason='Can\'t send signals without stopping '
                                       'whole process on windows')


class TestUpdater(object):
    message_count = 0
    received = None
    attempts = 0
    err_handler_called = Event()
    cb_handler_called = Event()

    @pytest.fixture(autouse=True)
    def reset(self):
        self.message_count = 0
        self.received = None
        self.attempts = 0
        self.err_handler_called.clear()
        self.cb_handler_called.clear()

    def error_handler(self, bot, update, error):
        self.received = error.message
        self.err_handler_called.set()

    def callback(self, bot, update):
        self.received = update.message.text
        self.cb_handler_called.set()

    # TODO: test clean= argument of Updater._bootstrap

    @pytest.mark.parametrize(('error',),
                             argvalues=[(TelegramError('Test Error 2'),),
                                        (Unauthorized('Test Unauthorized'),)],
                             ids=('TelegramError', 'Unauthorized'))
    def test_get_updates_normal_err(self, monkeypatch, updater, error):
        def test(*args, **kwargs):
            raise error

        monkeypatch.setattr('telegram.Bot.get_updates', test)
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        updater.dispatcher.add_error_handler(self.error_handler)
        updater.start_polling(0.01)

        # Make sure that the error handler was called
        self.err_handler_called.wait()
        assert self.received == error.message

        # Make sure that Updater polling thread keeps running
        self.err_handler_called.clear()
        self.err_handler_called.wait()

    def test_get_updates_bailout_err(self, monkeypatch, updater, caplog):
        error = InvalidToken()

        def test(*args, **kwargs):
            raise error

        with caplog.at_level(logging.DEBUG):
            monkeypatch.setattr('telegram.Bot.get_updates', test)
            monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
            updater.dispatcher.add_error_handler(self.error_handler)
            updater.start_polling(0.01)
            assert self.err_handler_called.wait(1) is not True

        sleep(1)
        # NOTE: This test might hit a race condition and fail (though the 1 seconds delay above
        #       should work around it).
        # NOTE: Checking Updater.running is problematic because it is not set to False when there's
        #       an unhandled exception.
        # TODO: We should have a way to poll Updater status and decide if it's running or not.
        assert any('unhandled exception in updater' in rec.getMessage() for rec in
                   caplog.get_records('call'))

    @pytest.mark.parametrize(('error',),
                             argvalues=[(RetryAfter(0.01),),
                                        (TimedOut(),)],
                             ids=('RetryAfter', 'TimedOut'))
    def test_get_updates_retries(self, monkeypatch, updater, error):
        event = Event()

        def test(*args, **kwargs):
            event.set()
            raise error

        monkeypatch.setattr('telegram.Bot.get_updates', test)
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        updater.dispatcher.add_error_handler(self.error_handler)
        updater.start_polling(0.01)

        # Make sure that get_updates was called, but not the error handler
        event.wait()
        assert self.err_handler_called.wait(0.5) is not True
        assert self.received != error.message

        # Make sure that Updater polling thread keeps running
        event.clear()
        event.wait()
        assert self.err_handler_called.wait(0.5) is not True

    def test_webhook(self, monkeypatch, updater):
        q = Queue()
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.Bot.delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port for travis
        updater.start_webhook(
            ip,
            port,
            url_path='TOKEN')
        sleep(.2)
        try:
            # Now, we send an update to the server via urlopen
            update = Update(1, message=Message(1, User(1, '', False), None, Chat(1, ''),
                                               text='Webhook'))
            self._send_webhook_msg(ip, port, update.to_json(), 'TOKEN')
            sleep(.2)
            assert q.get(False) == update

            # Returns 404 if path is incorrect
            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(ip, port, None, 'webookhandler.py')
            assert excinfo.value.code == 404

            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(ip, port, None, 'webookhandler.py',
                                       get_method=lambda: 'HEAD')
            assert excinfo.value.code == 404

            # Test multiple shutdown() calls
            updater.httpd.shutdown()
        finally:
            updater.httpd.shutdown()
            sleep(.2)
            assert not updater.httpd.is_running
            updater.stop()

    def test_webhook_ssl(self, monkeypatch, updater):
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.Bot.delete_webhook', lambda *args, **kwargs: True)
        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port for travis
        tg_err = False
        try:
            updater._start_webhook(
                ip,
                port,
                url_path='TOKEN',
                cert='./tests/test_updater.py',
                key='./tests/test_updater.py',
                bootstrap_retries=0,
                clean=False,
                webhook_url=None,
                allowed_updates=None)
        except TelegramError:
            tg_err = True
        assert tg_err

    def test_webhook_no_ssl(self, monkeypatch, updater):
        q = Queue()
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.Bot.delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port for travis
        updater.start_webhook(ip, port, webhook_url=None)
        sleep(.2)

        # Now, we send an update to the server via urlopen
        update = Update(1, message=Message(1, User(1, '', False), None, Chat(1, ''),
                                           text='Webhook 2'))
        self._send_webhook_msg(ip, port, update.to_json())
        sleep(.2)
        assert q.get(False) == update
        updater.stop()

    @pytest.mark.parametrize(('error',),
                             argvalues=[(TelegramError(''),)],
                             ids=('TelegramError',))
    def test_bootstrap_retries_success(self, monkeypatch, updater, error):
        retries = 2

        def attempt(_, *args, **kwargs):
            if self.attempts < retries:
                self.attempts += 1
                raise error

        monkeypatch.setattr('telegram.Bot.set_webhook', attempt)

        updater.running = True
        updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == retries

    @pytest.mark.parametrize(('error', 'attempts'),
                             argvalues=[(TelegramError(''), 2),
                                        (Unauthorized(''), 1),
                                        (InvalidToken(), 1)],
                             ids=('TelegramError', 'Unauthorized', 'InvalidToken'))
    def test_bootstrap_retries_error(self, monkeypatch, updater, error, attempts):
        retries = 1

        def attempt(_, *args, **kwargs):
            self.attempts += 1
            raise error

        monkeypatch.setattr('telegram.Bot.set_webhook', attempt)

        updater.running = True
        with pytest.raises(type(error)):
            updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == attempts

    def test_webhook_invalid_posts(self, updater):
        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # select random port for travis
        thr = Thread(
            target=updater._start_webhook,
            args=(ip, port, '', None, None, 0, False, None, None))
        thr.start()

        sleep(.2)

        try:
            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(ip, port, '<root><bla>data</bla></root>',
                                       content_type='application/xml')
            assert excinfo.value.code == 403

            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(ip, port, 'dummy-payload', content_len=-2)
            assert excinfo.value.code == 500

            # TODO: prevent urllib or the underlying from adding content-length
            # with pytest.raises(HTTPError) as excinfo:
            #     self._send_webhook_msg(ip, port, 'dummy-payload', content_len=None)
            # assert excinfo.value.code == 411

            with pytest.raises(HTTPError):
                self._send_webhook_msg(ip, port, 'dummy-payload', content_len='not-a-number')
            assert excinfo.value.code == 500

        finally:
            updater.httpd.shutdown()
            thr.join()

    def _send_webhook_msg(self,
                          ip,
                          port,
                          payload_str,
                          url_path='',
                          content_len=-1,
                          content_type='application/json',
                          get_method=None):
        headers = {'content-type': content_type, }

        if not payload_str:
            content_len = None
            payload = None
        else:
            payload = bytes(payload_str, encoding='utf-8')

        if content_len == -1:
            content_len = len(payload)

        if content_len is not None:
            headers['content-length'] = str(content_len)

        url = 'http://{ip}:{port}/{path}'.format(ip=ip, port=port, path=url_path)

        req = Request(url, data=payload, headers=headers)

        if get_method is not None:
            req.get_method = get_method

        return urlopen(req)

    def signal_sender(self, updater):
        sleep(0.2)
        while not updater.running:
            sleep(0.2)

        os.kill(os.getpid(), signal.SIGTERM)

    @signalskip
    def test_idle(self, updater, caplog):
        updater.start_polling(0.01)
        Thread(target=partial(self.signal_sender, updater=updater)).start()

        with caplog.at_level(logging.INFO):
            updater.idle()

        rec = caplog.records[-1]
        assert rec.msg.startswith('Received signal {}'.format(signal.SIGTERM))
        assert rec.levelname == 'INFO'

        # If we get this far, idle() ran through
        sleep(.5)
        assert updater.running is False

    @signalskip
    def test_user_signal(self, updater):
        temp_var = {'a': 0}

        def user_signal_inc(signum, frame):
            temp_var['a'] = 1

        updater.user_sig_handler = user_signal_inc
        updater.start_polling(0.01)
        Thread(target=partial(self.signal_sender, updater=updater)).start()
        updater.idle()
        # If we get this far, idle() ran through
        sleep(.5)
        assert updater.running is False
        assert temp_var['a'] != 0

    def test_create_bot(self):
        updater = Updater('123:abcd')
        assert updater.bot is not None

    def test_mutual_exclude_token_bot(self):
        bot = Bot('123:zyxw')
        with pytest.raises(ValueError):
            Updater(token='123:abcd', bot=bot)

    def test_no_token_or_bot(self):
        with pytest.raises(ValueError):
            Updater()

    def test_mutual_exclude_bot_private_key(self):
        bot = Bot('123:zyxw')
        with pytest.raises(ValueError):
            Updater(bot=bot, private_key=b'key')
