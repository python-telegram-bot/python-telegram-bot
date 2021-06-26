#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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
import asyncio
import logging
import os
import signal
import sys
import threading
from contextlib import contextmanager

from flaky import flaky
from functools import partial
from queue import Queue
from random import randrange
from threading import Thread, Event
from time import sleep

from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from telegram import (
    TelegramError,
    Message,
    User,
    Chat,
    Update,
    Bot,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.error import Unauthorized, InvalidToken, TimedOut, RetryAfter
from telegram.ext import (
    Updater,
    Dispatcher,
    DictPersistence,
    Defaults,
    InvalidCallbackData,
    ExtBot,
)
from telegram.utils.deprecate import TelegramDeprecationWarning
from telegram.ext.utils.webhookhandler import WebhookServer

signalskip = pytest.mark.skipif(
    sys.platform == 'win32',
    reason="Can't send signals without stopping whole process on windows",
)


ASYNCIO_LOCK = threading.Lock()


@contextmanager
def set_asyncio_event_loop(loop):
    with ASYNCIO_LOCK:
        try:
            orig_lop = asyncio.get_event_loop()
        except RuntimeError:
            orig_lop = None
        asyncio.set_event_loop(loop)
        try:
            yield
        finally:
            asyncio.set_event_loop(orig_lop)


class TestUpdater:
    message_count = 0
    received = None
    attempts = 0
    err_handler_called = Event()
    cb_handler_called = Event()
    offset = 0
    test_flag = False

    def test_slot_behaviour(self, updater, mro_slots, recwarn):
        for at in updater.__slots__:
            at = f"_Updater{at}" if at.startswith('__') and not at.endswith('__') else at
            assert getattr(updater, at, 'err') != 'err', f"got extra slot '{at}'"
        assert not updater.__dict__, f"got missing slot(s): {updater.__dict__}"
        assert len(mro_slots(updater)) == len(set(mro_slots(updater))), "duplicate slot"
        updater.custom, updater.running = 'should give warning', updater.running
        assert len(recwarn) == 1 and 'custom' in str(recwarn[0].message), recwarn.list

        class CustomUpdater(Updater):
            pass  # Tests that setting custom attributes of Updater subclass doesn't raise warning

        a = CustomUpdater(updater.bot.token)
        a.my_custom = 'no error!'
        assert len(recwarn) == 1

        updater.__setattr__('__test', 'mangled success')
        assert getattr(updater, '_Updater__test', 'e') == 'mangled success', "mangling failed"

    @pytest.fixture(autouse=True)
    def reset(self):
        self.message_count = 0
        self.received = None
        self.attempts = 0
        self.err_handler_called.clear()
        self.cb_handler_called.clear()
        self.test_flag = False

    def error_handler(self, bot, update, error):
        self.received = error.message
        self.err_handler_called.set()

    def callback(self, bot, update):
        self.received = update.message.text
        self.cb_handler_called.set()

    def test_warn_arbitrary_callback_data(self, bot, recwarn):
        Updater(bot=bot, arbitrary_callback_data=True)
        assert len(recwarn) == 1
        assert 'Passing arbitrary_callback_data to an Updater' in str(recwarn[0].message)

    @pytest.mark.parametrize(
        ('error',),
        argvalues=[(TelegramError('Test Error 2'),), (Unauthorized('Test Unauthorized'),)],
        ids=('TelegramError', 'Unauthorized'),
    )
    def test_get_updates_normal_err(self, monkeypatch, updater, error):
        def test(*args, **kwargs):
            raise error

        monkeypatch.setattr(updater.bot, 'get_updates', test)
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        updater.dispatcher.add_error_handler(self.error_handler)
        updater.start_polling(0.01)

        # Make sure that the error handler was called
        self.err_handler_called.wait()
        assert self.received == error.message

        # Make sure that Updater polling thread keeps running
        self.err_handler_called.clear()
        self.err_handler_called.wait()

    @pytest.mark.filterwarnings('ignore:.*:pytest.PytestUnhandledThreadExceptionWarning')
    def test_get_updates_bailout_err(self, monkeypatch, updater, caplog):
        error = InvalidToken()

        def test(*args, **kwargs):
            raise error

        with caplog.at_level(logging.DEBUG):
            monkeypatch.setattr(updater.bot, 'get_updates', test)
            monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
            updater.dispatcher.add_error_handler(self.error_handler)
            updater.start_polling(0.01)
            assert self.err_handler_called.wait(1) is not True

        sleep(1)
        # NOTE: This test might hit a race condition and fail (though the 1 seconds delay above
        #       should work around it).
        # NOTE: Checking Updater.running is problematic because it is not set to False when there's
        #       an unhandled exception.
        # TODO: We should have a way to poll Updater status and decide if it's running or not.
        import pprint

        pprint.pprint([rec.getMessage() for rec in caplog.get_records('call')])
        assert any(
            f'unhandled exception in Bot:{updater.bot.id}:updater' in rec.getMessage()
            for rec in caplog.get_records('call')
        )

    @pytest.mark.parametrize(
        ('error',), argvalues=[(RetryAfter(0.01),), (TimedOut(),)], ids=('RetryAfter', 'TimedOut')
    )
    def test_get_updates_retries(self, monkeypatch, updater, error):
        event = Event()

        def test(*args, **kwargs):
            event.set()
            raise error

        monkeypatch.setattr(updater.bot, 'get_updates', test)
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
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

    @pytest.mark.parametrize('ext_bot', [True, False])
    def test_webhook(self, monkeypatch, updater, ext_bot):
        # Testing with both ExtBot and Bot to make sure any logic in WebhookHandler
        # that depends on this distinction works
        if ext_bot and not isinstance(updater.bot, ExtBot):
            updater.bot = ExtBot(updater.bot.token)
        if not ext_bot and not type(updater.bot) is Bot:
            updater.bot = Bot(updater.bot.token)

        q = Queue()
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        updater.start_webhook(ip, port, url_path='TOKEN')
        sleep(0.2)
        try:
            # Now, we send an update to the server via urlopen
            update = Update(
                1,
                message=Message(
                    1, None, Chat(1, ''), from_user=User(1, '', False), text='Webhook'
                ),
            )
            self._send_webhook_msg(ip, port, update.to_json(), 'TOKEN')
            sleep(0.2)
            assert q.get(False) == update

            # Returns 404 if path is incorrect
            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(ip, port, None, 'webookhandler.py')
            assert excinfo.value.code == 404

            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(
                    ip, port, None, 'webookhandler.py', get_method=lambda: 'HEAD'
                )
            assert excinfo.value.code == 404

            # Test multiple shutdown() calls
            updater.httpd.shutdown()
        finally:
            updater.httpd.shutdown()
            sleep(0.2)
            assert not updater.httpd.is_running
            updater.stop()

    @pytest.mark.parametrize('invalid_data', [True, False])
    def test_webhook_arbitrary_callback_data(self, monkeypatch, updater, invalid_data):
        """Here we only test one simple setup. telegram.ext.ExtBot.insert_callback_data is tested
        extensively in test_bot.py in conjunction with get_updates."""
        updater.bot.arbitrary_callback_data = True
        try:
            q = Queue()
            monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
            monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
            monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

            ip = '127.0.0.1'
            port = randrange(1024, 49152)  # Select random port
            updater.start_webhook(ip, port, url_path='TOKEN')
            sleep(0.2)
            try:
                # Now, we send an update to the server via urlopen
                reply_markup = InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(text='text', callback_data='callback_data')
                )
                if not invalid_data:
                    reply_markup = updater.bot.callback_data_cache.process_keyboard(reply_markup)

                message = Message(
                    1,
                    None,
                    None,
                    reply_markup=reply_markup,
                )
                update = Update(1, message=message)
                self._send_webhook_msg(ip, port, update.to_json(), 'TOKEN')
                sleep(0.2)
                received_update = q.get(False)
                assert received_update == update

                button = received_update.message.reply_markup.inline_keyboard[0][0]
                if invalid_data:
                    assert isinstance(button.callback_data, InvalidCallbackData)
                else:
                    assert button.callback_data == 'callback_data'

                # Test multiple shutdown() calls
                updater.httpd.shutdown()
            finally:
                updater.httpd.shutdown()
                sleep(0.2)
                assert not updater.httpd.is_running
                updater.stop()
        finally:
            updater.bot.arbitrary_callback_data = False
            updater.bot.callback_data_cache.clear_callback_data()
            updater.bot.callback_data_cache.clear_callback_queries()

    def test_start_webhook_no_warning_or_error_logs(self, caplog, updater, monkeypatch):
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        # prevent api calls from @info decorator when updater.bot.id is used in thread names
        monkeypatch.setattr(updater.bot, '_bot', User(id=123, first_name='bot', is_bot=True))
        monkeypatch.setattr(updater.bot, '_commands', [])

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        with caplog.at_level(logging.WARNING):
            updater.start_webhook(ip, port)
            updater.stop()
        assert not caplog.records

    def test_webhook_ssl(self, monkeypatch, updater):
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        tg_err = False
        try:
            updater._start_webhook(
                ip,
                port,
                url_path='TOKEN',
                cert='./tests/test_updater.py',
                key='./tests/test_updater.py',
                bootstrap_retries=0,
                drop_pending_updates=False,
                webhook_url=None,
                allowed_updates=None,
            )
        except TelegramError:
            tg_err = True
        assert tg_err

    def test_webhook_no_ssl(self, monkeypatch, updater):
        q = Queue()
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        updater.start_webhook(ip, port, webhook_url=None)
        sleep(0.2)

        # Now, we send an update to the server via urlopen
        update = Update(
            1,
            message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Webhook 2'),
        )
        self._send_webhook_msg(ip, port, update.to_json())
        sleep(0.2)
        assert q.get(False) == update
        updater.stop()

    def test_webhook_ssl_just_for_telegram(self, monkeypatch, updater):
        q = Queue()

        def set_webhook(**kwargs):
            self.test_flag.append(bool(kwargs.get('certificate')))
            return True

        orig_wh_server_init = WebhookServer.__init__

        def webhook_server_init(*args):
            self.test_flag = [args[-1] is None]
            orig_wh_server_init(*args)

        monkeypatch.setattr(updater.bot, 'set_webhook', set_webhook)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))
        monkeypatch.setattr(
            'telegram.ext.utils.webhookhandler.WebhookServer.__init__', webhook_server_init
        )

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        updater.start_webhook(ip, port, webhook_url=None, cert='./tests/test_updater.py')
        sleep(0.2)

        # Now, we send an update to the server via urlopen
        update = Update(
            1,
            message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Webhook 2'),
        )
        self._send_webhook_msg(ip, port, update.to_json())
        sleep(0.2)
        assert q.get(False) == update
        updater.stop()
        assert self.test_flag == [True, True]

    @pytest.mark.parametrize('pass_max_connections', [True, False])
    def test_webhook_max_connections(self, monkeypatch, updater, pass_max_connections):
        q = Queue()
        max_connections = 42

        def set_webhook(**kwargs):
            print(kwargs)
            self.test_flag = kwargs.get('max_connections') == (
                max_connections if pass_max_connections else 40
            )
            return True

        monkeypatch.setattr(updater.bot, 'set_webhook', set_webhook)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr('telegram.ext.Dispatcher.process_update', lambda _, u: q.put(u))

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        if pass_max_connections:
            updater.start_webhook(ip, port, webhook_url=None, max_connections=max_connections)
        else:
            updater.start_webhook(ip, port, webhook_url=None)

        sleep(0.2)

        # Now, we send an update to the server via urlopen
        update = Update(
            1,
            message=Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Webhook 2'),
        )
        self._send_webhook_msg(ip, port, update.to_json())
        sleep(0.2)
        assert q.get(False) == update
        updater.stop()
        assert self.test_flag is True

    @pytest.mark.parametrize(('error',), argvalues=[(TelegramError(''),)], ids=('TelegramError',))
    def test_bootstrap_retries_success(self, monkeypatch, updater, error):
        retries = 2

        def attempt(*args, **kwargs):
            if self.attempts < retries:
                self.attempts += 1
                raise error

        monkeypatch.setattr(updater.bot, 'set_webhook', attempt)

        updater.running = True
        updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == retries

    @pytest.mark.parametrize(
        ('error', 'attempts'),
        argvalues=[(TelegramError(''), 2), (Unauthorized(''), 1), (InvalidToken(), 1)],
        ids=('TelegramError', 'Unauthorized', 'InvalidToken'),
    )
    def test_bootstrap_retries_error(self, monkeypatch, updater, error, attempts):
        retries = 1

        def attempt(*args, **kwargs):
            self.attempts += 1
            raise error

        monkeypatch.setattr(updater.bot, 'set_webhook', attempt)

        updater.running = True
        with pytest.raises(type(error)):
            updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
        assert self.attempts == attempts

    @pytest.mark.parametrize('drop_pending_updates', (True, False))
    def test_bootstrap_clean_updates(self, monkeypatch, updater, drop_pending_updates):
        # As dropping pending updates is done by passing `drop_pending_updates` to
        # set_webhook, we just check that we pass the correct value
        self.test_flag = False

        def delete_webhook(**kwargs):
            self.test_flag = kwargs.get('drop_pending_updates') == drop_pending_updates

        monkeypatch.setattr(updater.bot, 'delete_webhook', delete_webhook)

        updater.running = True
        updater._bootstrap(
            1,
            drop_pending_updates=drop_pending_updates,
            webhook_url=None,
            allowed_updates=None,
            bootstrap_interval=0,
        )
        assert self.test_flag is True

    def test_deprecation_warnings_start_webhook(self, recwarn, updater, monkeypatch):
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        # prevent api calls from @info decorator when updater.bot.id is used in thread names
        monkeypatch.setattr(updater.bot, '_bot', User(id=123, first_name='bot', is_bot=True))
        monkeypatch.setattr(updater.bot, '_commands', [])

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        updater.start_webhook(ip, port, clean=True, force_event_loop=False)
        updater.stop()

        for warning in recwarn:
            print(warning)

        try:  # This is for flaky tests (there's an unclosed socket sometimes)
            recwarn.pop(ResourceWarning)  # internally iterates through recwarn.list and deletes it
        except AssertionError:
            pass

        assert len(recwarn) == 3
        assert str(recwarn[0].message).startswith('Old Handler API')
        assert str(recwarn[1].message).startswith('The argument `clean` of')
        assert str(recwarn[2].message).startswith('The argument `force_event_loop` of')

    def test_clean_deprecation_warning_polling(self, recwarn, updater, monkeypatch):
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)
        monkeypatch.setattr(updater.bot, 'delete_webhook', lambda *args, **kwargs: True)
        # prevent api calls from @info decorator when updater.bot.id is used in thread names
        monkeypatch.setattr(updater.bot, '_bot', User(id=123, first_name='bot', is_bot=True))
        monkeypatch.setattr(updater.bot, '_commands', [])

        updater.start_polling(clean=True)
        updater.stop()
        for msg in recwarn:
            print(msg)

        try:  # This is for flaky tests (there's an unclosed socket sometimes)
            recwarn.pop(ResourceWarning)  # internally iterates through recwarn.list and deletes it
        except AssertionError:
            pass

        assert len(recwarn) == 2
        assert str(recwarn[0].message).startswith('Old Handler API')
        assert str(recwarn[1].message).startswith('The argument `clean` of')

    def test_clean_drop_pending_mutually_exclusive(self, updater):
        with pytest.raises(TypeError, match='`clean` and `drop_pending_updates` are mutually'):
            updater.start_polling(clean=True, drop_pending_updates=False)

        with pytest.raises(TypeError, match='`clean` and `drop_pending_updates` are mutually'):
            updater.start_webhook(clean=True, drop_pending_updates=False)

    @flaky(3, 1)
    def test_webhook_invalid_posts(self, updater):
        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # select random port for travis
        thr = Thread(
            target=updater._start_webhook, args=(ip, port, '', None, None, 0, False, None, None)
        )
        thr.start()

        sleep(0.2)

        try:
            with pytest.raises(HTTPError) as excinfo:
                self._send_webhook_msg(
                    ip, port, '<root><bla>data</bla></root>', content_type='application/xml'
                )
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

    def _send_webhook_msg(
        self,
        ip,
        port,
        payload_str,
        url_path='',
        content_len=-1,
        content_type='application/json',
        get_method=None,
    ):
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

        url = f'http://{ip}:{port}/{url_path}'

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

        # There is a chance of a conflict when getting updates since there can be many tests
        # (bots) running simultaneously while testing in github actions.
        records = caplog.records.copy()  # To avoid iterating and removing at same time
        for idx, log in enumerate(records):
            print(log)
            msg = log.getMessage()
            if msg.startswith('Error while getting Updates: Conflict'):
                caplog.records.pop(idx)  # For stability

            if msg.startswith('No error handlers are registered'):
                caplog.records.pop(idx)

        assert len(caplog.records) == 2, caplog.records

        rec = caplog.records[-2]
        assert rec.getMessage().startswith(f'Received signal {signal.SIGTERM}')
        assert rec.levelname == 'INFO'

        rec = caplog.records[-1]
        assert rec.getMessage().startswith('Scheduler has been shut down')
        assert rec.levelname == 'INFO'

        # If we get this far, idle() ran through
        sleep(0.5)
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
        sleep(0.5)
        assert updater.running is False
        assert temp_var['a'] != 0

    def test_create_bot(self):
        updater = Updater('123:abcd')
        assert updater.bot is not None

    def test_mutual_exclude_token_bot(self):
        bot = Bot('123:zyxw')
        with pytest.raises(ValueError):
            Updater(token='123:abcd', bot=bot)

    def test_no_token_or_bot_or_dispatcher(self):
        with pytest.raises(ValueError):
            Updater()

    def test_mutual_exclude_bot_private_key(self):
        bot = Bot('123:zyxw')
        with pytest.raises(ValueError):
            Updater(bot=bot, private_key=b'key')

    def test_mutual_exclude_bot_dispatcher(self, bot):
        dispatcher = Dispatcher(bot, None)
        bot = Bot('123:zyxw')
        with pytest.raises(ValueError):
            Updater(bot=bot, dispatcher=dispatcher)

    def test_mutual_exclude_persistence_dispatcher(self, bot):
        dispatcher = Dispatcher(bot, None)
        persistence = DictPersistence()
        with pytest.raises(ValueError):
            Updater(dispatcher=dispatcher, persistence=persistence)

    def test_mutual_exclude_workers_dispatcher(self, bot):
        dispatcher = Dispatcher(bot, None)
        with pytest.raises(ValueError):
            Updater(dispatcher=dispatcher, workers=8)

    def test_mutual_exclude_use_context_dispatcher(self, bot):
        dispatcher = Dispatcher(bot, None)
        use_context = not dispatcher.use_context
        with pytest.raises(ValueError):
            Updater(dispatcher=dispatcher, use_context=use_context)

    def test_mutual_exclude_custom_context_dispatcher(self):
        dispatcher = Dispatcher(None, None)
        with pytest.raises(ValueError):
            Updater(dispatcher=dispatcher, context_types=True)

    def test_defaults_warning(self, bot):
        with pytest.warns(TelegramDeprecationWarning, match='no effect when a Bot is passed'):
            Updater(bot=bot, defaults=Defaults())
