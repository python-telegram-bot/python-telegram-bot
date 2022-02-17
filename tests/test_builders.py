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
import pytest

from telegram.request import HTTPXRequest
from .conftest import data_file, PRIVATE_KEY

from telegram.ext import (
    ApplicationBuilder,
    Defaults,
)
from telegram.ext._builders import _BOT_CHECKS


@pytest.fixture(scope='function')
def builder():
    return ApplicationBuilder()


class TestApplicationBuilder:
    @pytest.mark.parametrize(
        'method, description', _BOT_CHECKS, ids=[entry[0] for entry in _BOT_CHECKS]
    )
    def test_mutually_exclusive_for_bot(self, builder, method, description):
        # First test that e.g. `bot` can't be set if `request` was already set
        # We pass the private key since `private_key` is the only method that doesn't just save
        # the passed value
        getattr(builder, method)(data_file('private.key'))
        with pytest.raises(RuntimeError, match=f'`bot` may only be set, if no {description}'):
            builder.bot(None)

        # Now test that `request` can't be set if `bot` was already set
        builder = builder.__class__()
        builder.bot(None)
        with pytest.raises(RuntimeError, match=f'`{method}` may only be set, if no bot instance'):
            getattr(builder, method)(None)

    def test_mutually_exclusive_for_request(self, builder):
        builder.request(None)
        methods = (
            'connection_pool_size',
            'connect_timeout',
            'pool_timeout',
            'read_timeout',
            'write_timeout',
            'proxy_url',
            'bot',
            'updater',
        )

        for method in methods:
            with pytest.raises(
                RuntimeError, match=f'`{method}` may only be set, if no request instance'
            ):
                getattr(builder, method)(None)

        for method in methods:
            builder = ApplicationBuilder()
            getattr(builder, method)(1)
            with pytest.raises(RuntimeError, match='`request` may only be set, if no'):
                builder.request(None)

    def test_mutually_exclusive_for_get_updates_request(self, builder):
        builder.get_updates_request(None)
        methods = (
            'get_updates_connection_pool_size',
            'get_updates_connect_timeout',
            'get_updates_pool_timeout',
            'get_updates_read_timeout',
            'get_updates_write_timeout',
            'get_updates_proxy_url',
            'bot',
            'updater',
        )

        for method in methods:
            with pytest.raises(
                RuntimeError,
                match=f'`{method}` may only be set, if no get_updates_request instance',
            ):
                getattr(builder, method)(None)

        for method in methods:
            builder = ApplicationBuilder()
            getattr(builder, method)(1)
            with pytest.raises(RuntimeError, match='`get_updates_request` may only be set, if no'):
                builder.get_updates_request(None)

    def test_build_without_token(self, builder):
        with pytest.raises(RuntimeError, match='No bot token was set.'):
            builder.build()

    def test_build_custom_bot(self, builder, bot):
        builder.bot(bot)
        app = builder.build()
        assert app.bot is bot
        assert app.updater.bot is bot

    def test_all_bot_args_custom(self, builder, bot):
        defaults = Defaults()
        request = HTTPXRequest()
        get_updates_request = HTTPXRequest()
        builder.token(bot.token).base_url('base_url').base_file_url('base_file_url').private_key(
            PRIVATE_KEY
        ).defaults(defaults).arbitrary_callback_data(42).request(request).get_updates_request(
            get_updates_request
        )
        built_bot = builder.build().bot

        assert built_bot.token == bot.token
        assert built_bot.base_url == 'base_url' + bot.token
        assert built_bot.base_file_url == 'base_file_url' + bot.token
        assert built_bot.defaults is defaults
        assert built_bot.request is request
        assert built_bot._request[0] is get_updates_request
        assert built_bot.callback_data_cache.maxsize == 42

        builder = ApplicationBuilder()
        builder.connection_pool_size(1).connect_timeout(2).pool_timeout(3)
        # TODO: This test is not finished
        # builder.token(bot.token).request_kwargs({'connect_timeout': 42})
        # built_bot = builder.build().bot
        #
        # assert built_bot.token == bot.token
        # assert built_bot.request._connect_timeout == 42

    #
    # def test_all_dispatcher_args_custom(self, app, builder):
    #     job_queue = JobQueue()
    #     persistence = PicklePersistence('filename')
    #     context_types = ContextTypes()
    #     builder.bot(app.bot).update_queue(app.update_queue).exception_event(
    #         app.exception_event
    #     ).job_queue(job_queue).persistence(persistence).context_types(context_types).workers(3)
    #     dispatcher = builder.build()
    #
    #     assert dispatcher.bot is app.bot
    #     assert dispatcher.update_queue is app.update_queue
    #     assert dispatcher.exception_event is app.exception_event
    #     assert dispatcher.job_queue is job_queue
    #     assert dispatcher.job_queue.dispatcher is dispatcher
    #     assert dispatcher.persistence is persistence
    #     assert dispatcher.context_types is context_types
    #     assert dispatcher.workers == 3
    #
    # def test_all_updater_args_custom(self, app, builder):
    #     updater = (
    #         builder.bot(app.bot)
    #         .exception_event(app.exception_event)
    #         .update_queue(app.update_queue)
    #         .user_signal_handler(42)
    #         .build()
    #     )
    #
    #     assert updater.dispatcher is None
    #     assert updater.bot is app.bot
    #     assert updater.exception_event is app.exception_event
    #     assert updater.update_queue is app.update_queue
    #     assert updater.user_signal_handler == 42
    #
    # def test_connection_pool_size_with_workers(self, bot, builder):
    #     app = builder.token(bot.token).workers(42).build()
    #     assert app.workers == 42
    #     assert app.bot.request.con_pool_size == 46
    #
    # def test_connection_pool_size_warning(self, bot, builder, recwarn):
    #     builder.token(bot.token).workers(42).request_kwargs({'con_pool_size': 1})
    #     app = builder.build()
    #     assert app.workers == 42
    #     assert app.bot.request.con_pool_size == 1
    #
    #     assert len(recwarn) == 1
    #     message = str(recwarn[-1].message)
    #     assert 'smaller (1)' in message
    #     assert 'recommended value of 46.' in message
    #     assert recwarn[-1].filename == __file__, "wrong stacklevel"
    #
    # def test_custom_classes(self, bot, builder):
    #     class CustomApplication(Application):
    #         def __init__(self, arg, **kwargs):
    #             super().__init__(**kwargs)
    #             self.arg = arg
    #
    #     builder.application_class(CustomApplication, kwargs={'arg': 2}).token(bot.token)
    #
    #     obj = builder.build()
    #     assert isinstance(obj, CustomApplication)
    #     assert obj.arg == 2
    #
    # @pytest.mark.parametrize('input_type', ('bytes', 'str', 'Path'))
    # def test_all_private_key_input_types(self, builder, bot, input_type):
    #     private_key = Path('tests/data/private.key')
    #     password = Path('tests/data/private_key.password')
    #
    #     if input_type == 'bytes':
    #         private_key = private_key.read_bytes()
    #         password = password.read_bytes()
    #     if input_type == 'str':
    #         private_key = str(private_key)
    #         password = str(password)
    #
    #     builder.token(bot.token).private_key(
    #         private_key=private_key,
    #         password=password,
    #     )
    #     bot = builder.build().bot
    #     assert bot.private_key
