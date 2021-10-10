#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2021
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

"""
We mainly test on UpdaterBuilder because it has all methods that DispatcherBuilder already has
"""
from random import randint
from threading import Event

import pytest

from telegram.request import Request
from .conftest import PRIVATE_KEY

from telegram.ext import (
    UpdaterBuilder,
    DispatcherBuilder,
    Defaults,
    JobQueue,
    PicklePersistence,
    ContextTypes,
    Dispatcher,
    Updater,
)
from telegram.ext._builders import _BOT_CHECKS, _DISPATCHER_CHECKS, _BaseBuilder


@pytest.fixture(
    scope='function',
    params=[{'class': UpdaterBuilder}, {'class': DispatcherBuilder}],
    ids=['UpdaterBuilder', 'DispatcherBuilder'],
)
def builder(request):
    return request.param['class']()


class TestBuilder:
    @pytest.mark.parametrize('workers', [randint(1, 100) for _ in range(10)])
    def test_get_connection_pool_size(self, workers):
        assert _BaseBuilder._get_connection_pool_size(workers) == workers + 4

    @pytest.mark.parametrize(
        'method, description', _BOT_CHECKS, ids=[entry[0] for entry in _BOT_CHECKS]
    )
    def test_mutually_exclusive_for_bot(self, builder, method, description):
        if getattr(builder, method, None) is None:
            pytest.skip(f'{builder.__class__} has no method called {method}')

        # First that e.g. `bot` can't be set if `request` was already set
        getattr(builder, method)(1)
        with pytest.raises(RuntimeError, match=f'`bot` may only be set, if no {description}'):
            builder.bot(None)

        # Now test that `request` can't be set if `bot` was already set
        builder = builder.__class__()
        builder.bot(None)
        with pytest.raises(RuntimeError, match=f'`{method}` may only be set, if no bot instance'):
            getattr(builder, method)(None)

    @pytest.mark.parametrize(
        'method, description', _DISPATCHER_CHECKS, ids=[entry[0] for entry in _DISPATCHER_CHECKS]
    )
    def test_mutually_exclusive_for_dispatcher(self, builder, method, description):
        if isinstance(builder, DispatcherBuilder):
            pytest.skip('This test is only relevant for UpdaterBuilder')

        if getattr(builder, method, None) is None:
            pytest.skip(f'{builder.__class__} has no method called {method}')

        # First that e.g. `dispatcher` can't be set if `bot` was already set
        getattr(builder, method)(None)
        with pytest.raises(
            RuntimeError, match=f'`dispatcher` may only be set, if no {description}'
        ):
            builder.dispatcher(None)

        # Now test that `bot` can't be set if `dispatcher` was already set
        builder = builder.__class__()
        builder.dispatcher(1)
        with pytest.raises(
            RuntimeError, match=f'`{method}` may only be set, if no Dispatcher instance'
        ):
            getattr(builder, method)(None)

        # Finally test that `bot` *can* be set if `dispatcher` was set to None
        builder = builder.__class__()
        builder.dispatcher(None)
        if method != 'dispatcher_class':
            getattr(builder, method)(None)
        else:
            with pytest.raises(
                RuntimeError, match=f'`{method}` may only be set, if no Dispatcher instance'
            ):
                getattr(builder, method)(None)

    def test_mutually_exclusive_for_request(self, builder):
        builder.request(None)
        with pytest.raises(
            RuntimeError, match='`request_kwargs` may only be set, if no Request instance'
        ):
            builder.request_kwargs(None)

        builder = builder.__class__()
        builder.request_kwargs(None)
        with pytest.raises(RuntimeError, match='`request` may only be set, if no request_kwargs'):
            builder.request(None)

    def test_build_without_token(self, builder):
        with pytest.raises(RuntimeError, match='No bot token was set.'):
            builder.build()

    def test_build_custom_bot(self, builder, bot):
        builder.bot(bot)
        obj = builder.build()
        assert obj.bot is bot

        if isinstance(obj, Updater):
            assert obj.dispatcher.bot is bot
            assert obj.dispatcher.job_queue.dispatcher is obj.dispatcher
            assert obj.exception_event is obj.dispatcher.exception_event

    def test_build_custom_dispatcher(self, dp):
        updater = UpdaterBuilder().dispatcher(dp).build()
        assert updater.dispatcher is dp
        assert updater.bot is updater.dispatcher.bot
        assert updater.exception_event is dp.exception_event

    def test_build_no_dispatcher(self, bot):
        updater = UpdaterBuilder().dispatcher(None).token(bot.token).build()
        assert updater.dispatcher is None
        assert updater.bot.token == bot.token
        assert updater.bot.request.con_pool_size == 8
        assert isinstance(updater.exception_event, Event)

    def test_all_bot_args_custom(self, builder, bot):
        defaults = Defaults()
        request = Request(8)
        builder.token(bot.token).base_url('base_url').base_file_url('base_file_url').private_key(
            PRIVATE_KEY
        ).defaults(defaults).arbitrary_callback_data(42).request(request)
        built_bot = builder.build().bot

        assert built_bot.token == bot.token
        assert built_bot.base_url == 'base_url' + bot.token
        assert built_bot.base_file_url == 'base_file_url' + bot.token
        assert built_bot.defaults is defaults
        assert built_bot.request is request
        assert built_bot.callback_data_cache.maxsize == 42

        builder = builder.__class__()
        builder.token(bot.token).request_kwargs({'connect_timeout': 42})
        built_bot = builder.build().bot

        assert built_bot.token == bot.token
        assert built_bot.request._connect_timeout == 42

    def test_all_dispatcher_args_custom(self, dp):
        builder = DispatcherBuilder()

        job_queue = JobQueue()
        persistence = PicklePersistence('filename')
        context_types = ContextTypes()
        builder.bot(dp.bot).update_queue(dp.update_queue).exception_event(
            dp.exception_event
        ).job_queue(job_queue).persistence(persistence).context_types(context_types).workers(3)
        dispatcher = builder.build()

        assert dispatcher.bot is dp.bot
        assert dispatcher.update_queue is dp.update_queue
        assert dispatcher.exception_event is dp.exception_event
        assert dispatcher.job_queue is job_queue
        assert dispatcher.job_queue.dispatcher is dispatcher
        assert dispatcher.persistence is persistence
        assert dispatcher.context_types is context_types
        assert dispatcher.workers == 3

    def test_all_updater_args_custom(self, dp):
        updater = (
            UpdaterBuilder()
            .dispatcher(None)
            .bot(dp.bot)
            .exception_event(dp.exception_event)
            .update_queue(dp.update_queue)
            .user_signal_handler(42)
            .build()
        )

        assert updater.dispatcher is None
        assert updater.bot is dp.bot
        assert updater.exception_event is dp.exception_event
        assert updater.update_queue is dp.update_queue
        assert updater.user_signal_handler == 42

    def test_connection_pool_size_with_workers(self, bot, builder):
        obj = builder.token(bot.token).workers(42).build()
        dispatcher = obj if isinstance(obj, Dispatcher) else obj.dispatcher
        assert dispatcher.workers == 42
        assert dispatcher.bot.request.con_pool_size == 46

    def test_connection_pool_size_warning(self, bot, builder, recwarn):
        builder.token(bot.token).workers(42).request_kwargs({'con_pool_size': 1})
        obj = builder.build()
        dispatcher = obj if isinstance(obj, Dispatcher) else obj.dispatcher
        assert dispatcher.workers == 42
        assert dispatcher.bot.request.con_pool_size == 1

        assert len(recwarn) == 1
        message = str(recwarn[-1].message)
        assert 'smaller (1)' in message
        assert 'recommended value of 46.' in message
        assert recwarn[-1].filename == __file__, "wrong stacklevel"

    def test_custom_classes(self, bot, builder):
        class CustomDispatcher(Dispatcher):
            def __init__(self, arg, **kwargs):
                super().__init__(**kwargs)
                self.arg = arg

        class CustomUpdater(Updater):
            def __init__(self, arg, **kwargs):
                super().__init__(**kwargs)
                self.arg = arg

        builder.dispatcher_class(CustomDispatcher, kwargs={'arg': 2}).token(bot.token)
        if isinstance(builder, UpdaterBuilder):
            builder.updater_class(CustomUpdater, kwargs={'arg': 1})

        obj = builder.build()

        if isinstance(builder, UpdaterBuilder):
            assert isinstance(obj, CustomUpdater)
            assert obj.arg == 1
            assert isinstance(obj.dispatcher, CustomDispatcher)
            assert obj.dispatcher.arg == 2
        else:
            assert isinstance(obj, CustomDispatcher)
            assert obj.arg == 2
