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
import os
import signal
import sys
from queue import Queue
from random import randrange
from threading import Thread
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
from telegram.error import Unauthorized, InvalidToken
from telegram.ext import Updater

signalskip = pytest.mark.skipif(sys.platform == 'win32',
                                reason='Can\'t send signals without stopping '
                                       'whole process on windows')


@pytest.fixture(scope='function')
def updater(bot):
    up = Updater(bot=bot, workers=2)
    yield up
    if up.running:
        up.stop()


class TestUpdater(object):
    message_count = 0
    received = None
    attempts = 0

    @pytest.fixture(autouse=True)
    def reset(self):
        self.message_count = 0
        self.received = None
        self.attempts = 0

    def error_handler(self, bot, update, error):
        self.received = error.message

    def callback(self, bot, update):
        self.received = update.message.text

    # TODO: test clean= argument

    def test_error_on_get_updates(self, monkeypatch, updater):
        def test(*args, **kwargs):
            raise TelegramError('Test Error 2')

        monkeypatch.setattr('telegram.Bot.get_updates', test)
        monkeypatch.setattr('telegram.Bot.set_webhook', lambda *args, **kwargs: True)
        updater.dispatcher.add_error_handler(self.error_handler)
        updater.start_polling(0.01)
        sleep(.1)
        assert self.received == 'Test Error 2'

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
            url_path='TOKEN',
            cert='./tests/test_updater.py',
            key='./tests/test_updater.py', )
        sleep(.2)
        # SSL-Wrapping will fail, so we start the server without SSL
        thr = Thread(target=updater.httpd.serve_forever)
        thr.start()

        try:
            # Now, we send an update to the server via urlopen
            update = Update(1, message=Message(1, User(1, '', False), None, Chat(1, ''), text='Webhook'))
            self._send_webhook_msg(ip, port, update.to_json(), 'TOKEN')
            sleep(.2)
            assert q.get(False) == update

            response = self._send_webhook_msg(ip, port, None, 'webookhandler.py')
            assert b'' == response.read()
            assert 200 == response.code

            response = self._send_webhook_msg(ip, port, None, 'webookhandler.py',
                                              get_method=lambda: 'HEAD')

            assert b'' == response.read()
            assert 200 == response.code

            # Test multiple shutdown() calls
            updater.httpd.shutdown()
        finally:
            updater.httpd.shutdown()
            thr.join()

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
        update = Update(1, message=Message(1, User(1, '', False), None, Chat(1, ''), text='Webhook 2'))
        self._send_webhook_msg(ip, port, update.to_json())
        sleep(.2)
        assert q.get(False) == update

    def test_bootstrap_retries_success(self, monkeypatch, updater):
        retries = 2

        def attempt(_, *args, **kwargs):
            if self.attempts < retries:
                self.attempts += 1
                raise TelegramError('')

        monkeypatch.setattr('telegram.Bot.set_webhook', attempt)

        updater._bootstrap(retries, False, 'path', None)
        assert self.attempts == retries

    @pytest.mark.parametrize(('error', 'attempts'),
                             argvalues=[
                                 (TelegramError(''), 2),
                                 (Unauthorized(''), 1),
                                 (InvalidToken(), 1)
                             ],
                             ids=('TelegramError', 'Unauthorized', 'InvalidToken'))
    def test_bootstrap_retries_error(self, monkeypatch, updater, error, attempts):
        retries = 1

        def attempt(_, *args, **kwargs):
            self.attempts += 1
            raise error

        monkeypatch.setattr('telegram.Bot.set_webhook', attempt)

        with pytest.raises(type(error)):
            updater._bootstrap(retries, False, 'path', None)
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
            assert excinfo.value.code == 403

            # TODO: prevent urllib or the underlying from adding content-length
            # with pytest.raises(HTTPError) as excinfo:
            #     self._send_webhook_msg(ip, port, 'dummy-payload', content_len=None)
            # assert excinfo.value.code == 411

            with pytest.raises(HTTPError) as ctx:
                self._send_webhook_msg(ip, port, 'dummy-payload', content_len='not-a-number')
            assert excinfo.value.code == 403

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

    def signal_sender(self):
        sleep(0.2)
        os.kill(os.getpid(), signal.SIGTERM)

    @signalskip
    def test_idle(self, updater):
        updater.start_polling(0.01)
        Thread(target=self.signal_sender).start()
        updater.idle()
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
        Thread(target=self.signal_sender).start()
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
