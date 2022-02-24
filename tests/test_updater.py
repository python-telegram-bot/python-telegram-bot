#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
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
from http import HTTPStatus
from pathlib import Path
from random import randrange
from typing import Optional

import pytest
from httpx import AsyncClient, Response

from telegram import (
    Bot,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.error import InvalidToken, TelegramError, TimedOut, RetryAfter
from telegram.ext import (
    Updater,
    ExtBot,
    InvalidCallbackData,
)
from telegram.ext._utils.webhookhandler import WebhookServer
from telegram.request import HTTPXRequest
from tests.conftest import make_message_update, make_message, DictBot


class TestUpdater:
    message_count = 0
    received = None
    attempts = 0
    err_handler_called = None
    cb_handler_called = None
    offset = 0
    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.message_count = 0
        self.received = None
        self.attempts = 0
        self.err_handler_called = None
        self.cb_handler_called = None
        self.test_flag = False

    def error_callback(self, error):
        self.received = error
        self.err_handler_called.set()

    def callback(self, update, context):
        self.received = update.message.text
        self.cb_handler_called.set()

    @staticmethod
    async def _send_webhook_message(
        ip: str,
        port: int,
        payload_str: Optional[str],
        url_path: str = '',
        content_len: int = -1,
        content_type: str = 'application/json',
        get_method: str = None,
    ) -> Response:
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

        async with AsyncClient() as client:
            return await client.request(
                url=url, method=get_method or 'POST', data=payload, headers=headers
            )

    def test_slot_behaviour(self, updater, mro_slots):
        for at in updater.__slots__:
            at = f"_Updater{at}" if at.startswith('__') and not at.endswith('__') else at
            assert getattr(updater, at, 'err') != 'err', f"got extra slot '{at}'"
        assert len(mro_slots(updater)) == len(set(mro_slots(updater))), "duplicate slot"

    def test_init(self, bot):
        queue = asyncio.Queue()
        updater = Updater(bot=bot, update_queue=queue)
        assert updater.bot is bot
        assert updater.update_queue is queue

    @pytest.mark.asyncio
    async def test_initialize(self, bot, monkeypatch):
        async def initialize_bot(*args, **kwargs):
            self.test_flag = True

        async with Bot(bot.token) as test_bot:
            monkeypatch.setattr(test_bot, 'initialize', initialize_bot)

            updater = Updater(bot=test_bot, update_queue=asyncio.Queue())
            await updater.initialize()

        assert self.test_flag

    @pytest.mark.asyncio
    async def test_shutdown(self, bot, monkeypatch):
        async def shutdown_bot(*args, **kwargs):
            self.test_flag = True

        async with Bot(bot.token) as test_bot:
            monkeypatch.setattr(test_bot, 'shutdown', shutdown_bot)

            updater = Updater(bot=test_bot, update_queue=asyncio.Queue())
            await updater.initialize()
            await updater.shutdown()

        assert self.test_flag

    @pytest.mark.asyncio
    async def test_context_manager(self, monkeypatch, updater):
        async def initialize(*args, **kwargs):
            self.test_flag = ['initialize']

        async def shutdown(*args, **kwargs):
            self.test_flag.append('stop')

        monkeypatch.setattr(Updater, 'initialize', initialize)
        monkeypatch.setattr(Updater, 'shutdown', shutdown)

        async with updater:
            pass

        assert self.test_flag == ['initialize', 'stop']

    @pytest.mark.asyncio
    async def test_context_manager_exception_on_init(self, monkeypatch, updater):
        async def initialize(*args, **kwargs):
            raise RuntimeError('initialize')

        async def shutdown(*args):
            self.test_flag = 'stop'

        monkeypatch.setattr(Updater, 'initialize', initialize)
        monkeypatch.setattr(Updater, 'shutdown', shutdown)

        with pytest.raises(RuntimeError, match='initialize'):
            async with updater:
                pass

        assert self.test_flag == 'stop'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('drop_pending_updates', (True, False))
    async def test_polling_basic(self, monkeypatch, updater, drop_pending_updates):
        updates = asyncio.Queue()
        await updates.put(Update(update_id=1))
        await updates.put(Update(update_id=2))

        async def get_updates(*args, **kwargs):
            next_update = await updates.get()
            updates.task_done()
            return [next_update]

        orig_del_webhook = updater.bot.delete_webhook

        async def delete_webhook(*args, **kwargs):
            # Dropping pending updates is done by passing the parameter to delete_webhook
            if kwargs.get('drop_pending_updates'):
                self.message_count += 1
            return await orig_del_webhook(*args, **kwargs)

        monkeypatch.setattr(updater.bot, 'get_updates', get_updates)
        monkeypatch.setattr(updater.bot, 'delete_webhook', delete_webhook)

        async with updater:
            await updater.start_polling(drop_pending_updates=drop_pending_updates)
            assert updater.running
            await updates.join()
            await updater.stop()
            assert not updater.running
            assert not (await updater.bot.get_webhook_info()).url
            if drop_pending_updates:
                assert self.message_count == 1
            else:
                assert self.message_count == 0

            await updates.put(Update(update_id=3))
            await updates.put(Update(update_id=4))

            # We call the same logic twice to make sure that restarting the updater works as well
            await updater.start_polling(drop_pending_updates=drop_pending_updates)
            assert updater.running
            await updates.join()
            await updater.stop()
            assert not updater.running
            assert not (await updater.bot.get_webhook_info()).url

        self.received = []
        self.message_count = 0
        while not updater.update_queue.empty():
            update = updater.update_queue.get_nowait()
            self.message_count += 1
            self.received.append(update.update_id)

        assert self.message_count == 4
        assert self.received == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_start_polling_already_running(self, updater):
        async with updater:
            await updater.start_polling()
            task = asyncio.create_task(updater.start_polling())
            with pytest.raises(RuntimeError, match='already running'):
                await task
            await updater.stop()

    @pytest.mark.asyncio
    async def test_start_polling_get_updates_parameters(self, updater, monkeypatch):
        update_queue = asyncio.Queue()
        await update_queue.put(Update(update_id=1))

        expected = dict(
            timeout=10,
            read_timeout=2,
            write_timeout=DEFAULT_NONE,
            connect_timeout=DEFAULT_NONE,
            pool_timeout=DEFAULT_NONE,
            allowed_updates=None,
        )

        async def get_updates(*args, **kwargs):
            for key, value in expected.items():
                assert kwargs.get(key) == value
            await update_queue.get()
            update_queue.task_done()
            return []

        monkeypatch.setattr(updater.bot, 'get_updates', get_updates)

        async with updater:
            await updater.start_polling()
            await update_queue.join()
            await updater.stop()

            expected = dict(
                timeout=42,
                read_timeout=43,
                write_timeout=44,
                connect_timeout=45,
                pool_timeout=46,
                allowed_updates=['message'],
            )

            await update_queue.put(Update(update_id=1))
            await updater.start_polling(
                timeout=42,
                read_timeout=43,
                write_timeout=44,
                connect_timeout=45,
                pool_timeout=46,
                allowed_updates=['message'],
            )
            await update_queue.join()
            await updater.stop()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('exception_class', (InvalidToken, TelegramError))
    @pytest.mark.parametrize('retries', (3, 0))
    async def test_start_polling_bootstrap_retries(
        self, updater, monkeypatch, exception_class, retries
    ):
        async def do_request(*args, **kwargs):
            self.message_count += 1
            raise exception_class(str(self.message_count))

        monkeypatch.setattr(HTTPXRequest, 'do_request', do_request)

        async with updater:
            if exception_class == InvalidToken:
                with pytest.raises(InvalidToken, match='1'):
                    await updater.start_polling(bootstrap_retries=retries)
            else:
                with pytest.raises(TelegramError, match=str(retries + 1)):
                    await updater.start_polling(
                        bootstrap_retries=retries,
                    )

    @pytest.mark.parametrize(
        'error,callback',
        argvalues=[
            (TelegramError('TestMessage'), True),
            (RetryAfter(1), False),
            (TimedOut('TestMessage'), False),
        ],
        ids=('TelegramError', 'RetryAfter', 'TimedOut'),
    )
    @pytest.mark.asyncio
    async def test_start_polling_exceptions_and_error_callback(
        self, monkeypatch, updater, error, callback
    ):
        get_updates_event = asyncio.Event()

        async def get_updates(*args, **kwargs):
            # So that the main task has a chance to be called
            await asyncio.sleep(0)

            get_updates_event.set()
            raise error

        monkeypatch.setattr(updater.bot, 'get_updates', get_updates)
        monkeypatch.setattr(updater.bot, 'set_webhook', lambda *args, **kwargs: True)

        async with updater:
            self.err_handler_called = asyncio.Event()

            await updater.start_polling(error_callback=self.error_callback)
            await asyncio.sleep(1)

            if callback:
                # Make sure that the error handler was called
                assert self.err_handler_called.is_set()
                assert self.received == error
            # Make sure that get_updates was called
            assert get_updates_event.is_set()

            # Make sure that Updater polling keeps running
            self.err_handler_called.clear()
            get_updates_event.clear()
            await get_updates_event.wait()
            if callback:
                # Make sure that the error handler was called
                assert self.err_handler_called.is_set()
                assert self.received == error
            await updater.stop()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('ext_bot', [True, False])
    @pytest.mark.parametrize('drop_pending_updates', (True, False))
    async def test_webhook_basic(self, monkeypatch, updater, drop_pending_updates, ext_bot):
        # Testing with both ExtBot and Bot to make sure any logic in WebhookHandler
        # that depends on this distinction works
        if ext_bot and not isinstance(updater.bot, ExtBot):
            updater.bot = ExtBot(updater.bot.token)
        if not ext_bot and not type(updater.bot) is Bot:
            updater.bot = DictBot(updater.bot.token)

        async def delete_webhook(*args, **kwargs):
            # Dropping pending updates is done by passing the parameter to delete_webhook
            if kwargs.get('drop_pending_updates'):
                self.message_count += 1
            return True

        async def set_webhook(*args, **kwargs):
            return True

        monkeypatch.setattr(updater.bot, 'set_webhook', set_webhook)
        monkeypatch.setattr(updater.bot, 'delete_webhook', delete_webhook)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port

        async with updater:
            await updater.start_webhook(
                drop_pending_updates=drop_pending_updates,
                ip_address=ip,
                port=port,
                url_path='TOKEN',
            )
            assert updater.running

            # Now, we send an update to the server
            update = make_message_update('Webhook', message_factory=make_message)
            await self._send_webhook_message(ip, port, update.to_json(), 'TOKEN')
            assert (await updater.update_queue.get()).to_dict() == update.to_dict()

            # Returns Forbidden if wrong content types
            response = await self._send_webhook_message(
                ip, port, None, 'TOKEN', content_type='invalid'
            )
            assert response.status_code == HTTPStatus.FORBIDDEN

            # Returns Not Found if path is incorrect
            response = await self._send_webhook_message(ip, port, '123456', 'webhook_handler.py')
            assert response.status_code == HTTPStatus.NOT_FOUND

            # Returns METHOD_NOT_ALLOWED if method is not allowed
            response = await self._send_webhook_message(ip, port, None, 'TOKEN', get_method='HEAD')
            assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

            await updater.stop()
            assert not updater.running

            if drop_pending_updates:
                assert self.message_count == 1
            else:
                assert self.message_count == 0

            # We call the same logic twice to make sure that restarting the updater works as well
            await updater.start_webhook(
                drop_pending_updates=drop_pending_updates,
                ip_address=ip,
                port=port,
                url_path='TOKEN',
            )
            assert updater.running
            update = make_message_update('Webhook', message_factory=make_message)
            await self._send_webhook_message(ip, port, update.to_json(), 'TOKEN')
            assert (await updater.update_queue.get()).to_dict() == update.to_dict()
            await updater.stop()
            assert not updater.running

    @pytest.mark.asyncio
    async def test_start_webhook_already_running(self, updater, monkeypatch):
        async def return_true(*args, **kwargs):
            return True

        monkeypatch.setattr(updater.bot, 'set_webhook', return_true)
        monkeypatch.setattr(updater.bot, 'delete_webhook', return_true)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        async with updater:
            await updater.start_webhook(ip, port, url_path='TOKEN')
            task = asyncio.create_task(updater.start_webhook(ip, port, url_path='TOKEN'))
            with pytest.raises(RuntimeError, match='already running'):
                await task
            await updater.stop()

    @pytest.mark.parametrize('invalid_data', [True, False], ids=('invalid data', 'valid data'))
    @pytest.mark.asyncio
    async def test_webhook_arbitrary_callback_data(
        self, monkeypatch, updater, invalid_data, chat_id
    ):
        """Here we only test one simple setup. telegram.ext.ExtBot.insert_callback_data is tested
        extensively in test_bot.py in conjunction with get_updates."""
        updater.bot.arbitrary_callback_data = True

        async def return_true(*args, **kwargs):
            return True

        try:
            monkeypatch.setattr(updater.bot, 'set_webhook', return_true)
            monkeypatch.setattr(updater.bot, 'delete_webhook', return_true)

            ip = '127.0.0.1'
            port = randrange(1024, 49152)  # Select random port

            async with updater:
                await updater.start_webhook(ip, port, url_path='TOKEN')
                # Now, we send an update to the server
                reply_markup = InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(text='text', callback_data='callback_data')
                )
                if not invalid_data:
                    reply_markup = updater.bot.callback_data_cache.process_keyboard(reply_markup)

                update = make_message_update(
                    message='test_webhook_arbitrary_callback_data',
                    message_factory=make_message,
                    reply_markup=reply_markup,
                    user=updater.bot.bot,
                )

                await self._send_webhook_message(ip, port, update.to_json(), 'TOKEN')
                received_update = await updater.update_queue.get()

                assert received_update.update_id == update.update_id
                message_dict = update.message.to_dict()
                received_dict = received_update.message.to_dict()
                message_dict.pop('reply_markup')
                received_dict.pop('reply_markup')
                assert message_dict == received_dict

                button = received_update.message.reply_markup.inline_keyboard[0][0]
                if invalid_data:
                    assert isinstance(button.callback_data, InvalidCallbackData)
                else:
                    assert button.callback_data == 'callback_data'
        finally:
            updater.bot.arbitrary_callback_data = False
            updater.bot.callback_data_cache.clear_callback_data()
            updater.bot.callback_data_cache.clear_callback_queries()

    @pytest.mark.asyncio
    async def test_webhook_invalid_ssl(self, monkeypatch, updater):
        async def return_true(*args, **kwargs):
            return True

        monkeypatch.setattr(updater.bot, 'set_webhook', return_true)
        monkeypatch.setattr(updater.bot, 'delete_webhook', return_true)

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        async with updater:
            with pytest.raises(TelegramError, match='Invalid SSL'):
                await updater.start_webhook(
                    ip,
                    port,
                    url_path='TOKEN',
                    cert=Path(__file__).as_posix(),
                    key=Path(__file__).as_posix(),
                    bootstrap_retries=0,
                    drop_pending_updates=False,
                    webhook_url=None,
                    allowed_updates=None,
                )

    @pytest.mark.asyncio
    async def test_webhook_ssl_just_for_telegram(self, monkeypatch, updater):
        """Here we just test that the SSL info is pased to Telegram, but __not__ to the the
        webhook server"""

        async def set_webhook(**kwargs):
            self.test_flag.append(bool(kwargs.get('certificate')))
            return True

        async def return_true(*args, **kwargs):
            return True

        orig_wh_server_init = WebhookServer.__init__

        def webhook_server_init(*args, **kwargs):
            self.test_flag = [kwargs.get('ssl_ctx') is None]
            orig_wh_server_init(*args, **kwargs)

        monkeypatch.setattr(updater.bot, 'set_webhook', set_webhook)
        monkeypatch.setattr(updater.bot, 'delete_webhook', return_true)
        monkeypatch.setattr(
            'telegram.ext._utils.webhookhandler.WebhookServer.__init__', webhook_server_init
        )

        ip = '127.0.0.1'
        port = randrange(1024, 49152)  # Select random port
        async with updater:
            await updater.start_webhook(ip, port, webhook_url=None, cert=Path(__file__).as_posix())

            # Now, we send an update to the server
            update = make_message_update(message='test_message', message_factory=make_message)
            await self._send_webhook_message(ip, port, update.to_json())
            assert (await updater.update_queue.get()).to_dict() == update.to_dict()
            assert self.test_flag == [True, True]

    # @pytest.mark.parametrize(('error',),argvalues=[(TelegramError(''),)], ids=('TelegramError',))
    # def test_bootstrap_retries_success(self, monkeypatch, updater, error):
    #     retries = 2
    #
    #     def attempt(*args, **kwargs):
    #         if self.attempts < retries:
    #             self.attempts += 1
    #             raise error
    #
    #     monkeypatch.setattr(updater.bot, 'set_webhook', attempt)
    #
    #     updater.running = True
    #     updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
    #     assert self.attempts == retries
    #
    # @pytest.mark.parametrize(
    #     ('error', 'attempts'),
    #     argvalues=[(TelegramError(''), 2), (Unauthorized(''), 1), (InvalidToken(), 1)],
    #     ids=('TelegramError', 'Unauthorized', 'InvalidToken'),
    # )
    # def test_bootstrap_retries_error(self, monkeypatch, updater, error, attempts):
    #     retries = 1
    #
    #     def attempt(*args, **kwargs):
    #         self.attempts += 1
    #         raise error
    #
    #     monkeypatch.setattr(updater.bot, 'set_webhook', attempt)
    #
    #     updater.running = True
    #     with pytest.raises(type(error)):
    #         updater._bootstrap(retries, False, 'path', None, bootstrap_interval=0)
    #     assert self.attempts == attempts
    #
    # @pytest.mark.parametrize('drop_pending_updates', (True, False))
    # def test_bootstrap_clean_updates(self, monkeypatch, updater, drop_pending_updates):
    #     # As dropping pending updates is done by passing `drop_pending_updates` to
    #     # set_webhook, we just check that we pass the correct value
    #     self.test_flag = False
    #
    #     def delete_webhook(**kwargs):
    #         self.test_flag = kwargs.get('drop_pending_updates') == drop_pending_updates
    #
    #     monkeypatch.setattr(updater.bot, 'delete_webhook', delete_webhook)
    #
    #     updater.running = True
    #     updater._bootstrap(
    #         1,
    #         drop_pending_updates=drop_pending_updates,
    #         webhook_url=None,
    #         allowed_updates=None,
    #         bootstrap_interval=0,
    #     )
    #     assert self.test_flag is True
    #
    # @flaky(3, 1)
    # def test_webhook_invalid_posts(self, updater):
    #     ip = '127.0.0.1'
    #     port = randrange(1024, 49152)  # select random port for travis
    #     thr = Thread(
    #         target=updater._start_webhook, args=(ip, port, '', None, None, 0, False, None, None)
    #     )
    #     thr.start()
    #
    #     sleep(0.2)
    #
    #     try:
    #         with pytest.raises(HTTPError) as excinfo:
    #             self._send_webhook_msg(
    #                 ip, port, '<root><bla>data</bla></root>', content_type='application/xml'
    #             )
    #         assert excinfo.value.code == 403
    #
    #         with pytest.raises(HTTPError) as excinfo:
    #             self._send_webhook_msg(ip, port, 'dummy-payload', content_len=-2)
    #         assert excinfo.value.code == 500
    #
    #         # TODO: prevent urllib or the underlying from adding content-length
    #         # with pytest.raises(HTTPError) as excinfo:
    #         #     self._send_webhook_msg(ip, port, 'dummy-payload', content_len=None)
    #         # assert excinfo.value.code == 411
    #
    #         with pytest.raises(HTTPError):
    #             self._send_webhook_msg(ip, port, 'dummy-payload', content_len='not-a-number')
    #         assert excinfo.value.code == 500
    #
    #     finally:
    #         updater.httpd.shutdown()
    #         thr.join()

    # TODO:
    # test_start_webhook_set/delete_webhook_parameters
    # test_start_webhook_bootstrap_retries
