#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2025
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
import inspect
from dataclasses import dataclass
from http import HTTPStatus

import httpx
import pytest

from telegram import Bot
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CallbackDataCache,
    ContextTypes,
    Defaults,
    ExtBot,
    JobQueue,
    PicklePersistence,
    Updater,
)
from telegram.ext._applicationbuilder import _BOT_CHECKS
from telegram.ext._baseupdateprocessor import SimpleUpdateProcessor
from telegram.request import HTTPXRequest
from tests.auxil.constants import PRIVATE_KEY
from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture
def builder():
    return ApplicationBuilder()


@pytest.mark.skipif(TEST_WITH_OPT_DEPS, reason="Optional dependencies are installed")
class TestApplicationBuilderNoOptDeps:
    @pytest.mark.filterwarnings("ignore::telegram.warnings.PTBUserWarning")
    def test_init(self, builder):
        builder.token("token")
        app = builder.build()
        assert app.job_queue is None


@pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="Optional dependencies not installed")
class TestApplicationBuilder:
    def test_slot_behaviour(self, builder):
        for attr in builder.__slots__:
            assert getattr(builder, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(builder)) == len(set(mro_slots(builder))), "duplicate slot"

    @pytest.mark.parametrize("get_updates", [True, False])
    def test_all_methods_request(self, builder, get_updates):
        arguments = inspect.signature(HTTPXRequest.__init__).parameters.keys()
        prefix = "get_updates_" if get_updates else ""
        for argument in arguments:
            if argument in ("self", "httpx_kwargs"):
                continue
            if argument == "media_write_timeout" and get_updates:
                # get_updates never makes media requests
                continue
            assert hasattr(builder, prefix + argument), f"missing method {prefix}{argument}"

    @pytest.mark.parametrize("bot_class", [Bot, ExtBot])
    def test_all_methods_bot(self, builder, bot_class):
        arguments = inspect.signature(bot_class.__init__).parameters.keys()
        for argument in arguments:
            if argument == "self":
                continue
            if argument == "private_key_password":
                argument = "private_key"  # noqa: PLW2901
            assert hasattr(builder, argument), f"missing method {argument}"

    def test_all_methods_application(self, builder):
        arguments = inspect.signature(Application.__init__).parameters.keys()
        for argument in arguments:
            if argument == "self":
                continue
            if argument == "update_processor":
                argument = "concurrent_updates"  # noqa: PLW2901
            assert hasattr(builder, argument), f"missing method {argument}"

    def test_job_queue_init_exception(self, monkeypatch):
        def init_raises_runtime_error(*args, **kwargs):
            raise RuntimeError("RuntimeError")

        monkeypatch.setattr(JobQueue, "__init__", init_raises_runtime_error)

        with pytest.raises(RuntimeError, match="RuntimeError"):
            ApplicationBuilder()

    def test_build_without_token(self, builder):
        with pytest.raises(RuntimeError, match="No bot token was set."):
            builder.build()

    def test_build_custom_bot(self, builder, bot):
        builder.bot(bot)
        app = builder.build()
        assert app.bot is bot
        assert app.updater.bot is bot

    def test_default_values(self, bot, monkeypatch, builder):
        @dataclass
        class Client:
            timeout: object
            proxy: object
            limits: object
            http1: object
            http2: object
            transport: object = None

        monkeypatch.setattr(httpx, "AsyncClient", Client)

        app = builder.token(bot.token).build()

        assert isinstance(app, Application)
        assert isinstance(app.update_processor, SimpleUpdateProcessor)
        assert app.update_processor.max_concurrent_updates == 1

        assert isinstance(app.bot, ExtBot)
        assert isinstance(app.bot.request, HTTPXRequest)
        assert "api.telegram.org" in app.bot.base_url
        assert bot.token in app.bot.base_url
        assert "api.telegram.org" in app.bot.base_file_url
        assert bot.token in app.bot.base_file_url
        assert app.bot.private_key is None
        assert app.bot.callback_data_cache is None
        assert app.bot.defaults is None
        assert app.bot.rate_limiter is None
        assert app.bot.local_mode is False

        get_updates_client = app.bot._request[0]._client
        assert get_updates_client.limits == httpx.Limits(
            max_connections=1, max_keepalive_connections=1
        )
        assert get_updates_client.proxy is None
        assert get_updates_client.timeout == httpx.Timeout(
            connect=5.0, read=5.0, write=5.0, pool=1.0
        )
        assert get_updates_client.http1 is True
        assert not get_updates_client.http2

        client = app.bot.request._client
        assert client.limits == httpx.Limits(max_connections=256, max_keepalive_connections=256)
        assert client.proxy is None
        assert client.timeout == httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=1.0)
        assert client.http1 is True
        assert not client.http2

        assert isinstance(app.update_queue, asyncio.Queue)
        assert isinstance(app.updater, Updater)
        assert app.updater.bot is app.bot
        assert app.updater.update_queue is app.update_queue

        assert isinstance(app.job_queue, JobQueue)
        assert app.job_queue.application is app

        assert app.persistence is None
        assert app.post_init is None
        assert app.post_shutdown is None
        assert app.post_stop is None

    @pytest.mark.parametrize(
        ("method", "description"), _BOT_CHECKS, ids=[entry[0] for entry in _BOT_CHECKS]
    )
    def test_mutually_exclusive_for_bot(self, builder, method, description):
        # First test that e.g. `bot` can't be set if `request` was already set
        # We pass the private key since `private_key` is the only method that doesn't just save
        # the passed value
        getattr(builder, method)(data_file("private.key"))
        with pytest.raises(RuntimeError, match=f"`bot` may only be set, if no {description}"):
            builder.bot(None)

        # Now test that `request` can't be set if `bot` was already set
        builder = builder.__class__()
        builder.bot(None)
        with pytest.raises(RuntimeError, match=f"`{method}` may only be set, if no bot instance"):
            getattr(builder, method)(data_file("private.key"))

    @pytest.mark.parametrize(
        "method",
        [
            "connection_pool_size",
            "connect_timeout",
            "pool_timeout",
            "read_timeout",
            "write_timeout",
            "media_write_timeout",
            "proxy",
            "socket_options",
            "bot",
            "updater",
            "http_version",
        ],
    )
    def test_mutually_exclusive_for_request(self, builder, method):
        builder.request(1)

        with pytest.raises(
            RuntimeError, match=f"`{method}` may only be set, if no request instance"
        ):
            getattr(builder, method)(data_file("private.key"))

        builder = ApplicationBuilder()
        getattr(builder, method)(1)
        with pytest.raises(RuntimeError, match="`request` may only be set, if no"):
            builder.request(1)

    @pytest.mark.parametrize(
        "method",
        [
            "get_updates_connection_pool_size",
            "get_updates_connect_timeout",
            "get_updates_pool_timeout",
            "get_updates_read_timeout",
            "get_updates_write_timeout",
            "get_updates_proxy",
            "get_updates_socket_options",
            "get_updates_http_version",
            "bot",
            "updater",
        ],
    )
    def test_mutually_exclusive_for_get_updates_request(self, builder, method):
        builder.get_updates_request(1)

        with pytest.raises(
            RuntimeError,
            match=f"`{method}` may only be set, if no get_updates_request instance",
        ):
            getattr(builder, method)(data_file("private.key"))

        builder = ApplicationBuilder()
        getattr(builder, method)(1)
        with pytest.raises(RuntimeError, match="`get_updates_request` may only be set, if no"):
            builder.get_updates_request(1)

    @pytest.mark.parametrize(
        "method",
        [
            "get_updates_connection_pool_size",
            "get_updates_connect_timeout",
            "get_updates_pool_timeout",
            "get_updates_read_timeout",
            "get_updates_write_timeout",
            "get_updates_proxy",
            "get_updates_socket_options",
            "get_updates_http_version",
            "connection_pool_size",
            "connect_timeout",
            "pool_timeout",
            "read_timeout",
            "write_timeout",
            "media_write_timeout",
            "proxy",
            "socket_options",
            "http_version",
            "bot",
            "update_queue",
            "rate_limiter",
        ]
        + [entry[0] for entry in _BOT_CHECKS],
    )
    def test_mutually_exclusive_for_updater(self, builder, method):
        builder.updater(1)

        with pytest.raises(
            RuntimeError,
            match=f"`{method}` may only be set, if no updater",
        ):
            getattr(builder, method)(data_file("private.key"))

        builder = ApplicationBuilder()
        getattr(builder, method)(data_file("private.key"))

        with pytest.raises(RuntimeError, match=f"`updater` may only be set, if no {method}"):
            builder.updater(1)

    @pytest.mark.parametrize(
        "method",
        [
            "get_updates_connection_pool_size",
            "get_updates_connect_timeout",
            "get_updates_pool_timeout",
            "get_updates_read_timeout",
            "get_updates_write_timeout",
            "get_updates_proxy",
            "get_updates_socket_options",
            "get_updates_http_version",
            "connection_pool_size",
            "connect_timeout",
            "pool_timeout",
            "read_timeout",
            "write_timeout",
            "media_write_timeout",
            "proxy",
            "socket_options",
            "bot",
            "http_version",
        ]
        + [entry[0] for entry in _BOT_CHECKS],
    )
    def test_mutually_non_exclusive_for_updater(self, builder, method):
        # If no updater is to be used, all these parameters should be settable
        # Since the parameters themself are tested in the other tests, we here just make sure
        # that no exception is raised
        builder.updater(None)
        getattr(builder, method)(data_file("private.key"))

        builder = ApplicationBuilder()
        getattr(builder, method)(data_file("private.key"))
        builder.updater(None)

    def test_all_bot_args_custom(
        self,
        builder,
        bot,
        monkeypatch,
    ):
        # Only socket_options is tested in a standalone test, since that's easier
        defaults = Defaults()
        request = HTTPXRequest()
        get_updates_request = HTTPXRequest()
        rate_limiter = AIORateLimiter()
        builder.token(bot.token).base_url("base_url").base_file_url("base_file_url").private_key(
            PRIVATE_KEY
        ).defaults(defaults).arbitrary_callback_data(42).request(request).get_updates_request(
            get_updates_request
        ).rate_limiter(
            rate_limiter
        ).local_mode(
            True
        )
        built_bot = builder.build().bot

        # In the following we access some private attributes of bot and request. this is not
        # really nice as we want to test the public interface, but here it's hard to ensure by
        # other means that the parameters are passed correctly

        assert built_bot.token == bot.token
        assert built_bot.base_url == "base_url" + bot.token
        assert built_bot.base_file_url == "base_file_url" + bot.token
        assert built_bot.defaults is defaults
        assert built_bot.request is request
        assert built_bot._request[0] is get_updates_request
        assert built_bot.callback_data_cache.maxsize == 42
        assert built_bot.private_key
        assert built_bot.rate_limiter is rate_limiter
        assert built_bot.local_mode is True

        @dataclass
        class Client:
            timeout: object
            proxy: object
            limits: object
            http1: object
            http2: object
            transport: object = None

        original_init = HTTPXRequest.__init__
        media_write_timeout = []

        def init_httpx_request(self_, *args, **kwargs):
            media_write_timeout.append(kwargs.get("media_write_timeout"))
            original_init(self_, *args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", Client)
        monkeypatch.setattr(HTTPXRequest, "__init__", init_httpx_request)

        builder = ApplicationBuilder().token(bot.token)
        builder.connection_pool_size(1).connect_timeout(2).pool_timeout(3).read_timeout(
            4
        ).write_timeout(5).media_write_timeout(6).http_version("1.1").proxy("proxy")
        app = builder.build()
        client = app.bot.request._client

        assert client.timeout == httpx.Timeout(pool=3, connect=2, read=4, write=5)
        assert client.limits == httpx.Limits(max_connections=1, max_keepalive_connections=1)
        assert client.proxy == "proxy"
        assert client.http1 is True
        assert client.http2 is False
        assert media_write_timeout == [6, None]

        media_write_timeout.clear()
        builder = ApplicationBuilder().token(bot.token)
        builder.get_updates_connection_pool_size(1).get_updates_connect_timeout(
            2
        ).get_updates_pool_timeout(3).get_updates_read_timeout(4).get_updates_write_timeout(
            5
        ).get_updates_http_version(
            "1.1"
        ).get_updates_proxy(
            "get_updates_proxy"
        )
        app = builder.build()
        client = app.bot._request[0]._client

        assert client.timeout == httpx.Timeout(pool=3, connect=2, read=4, write=5)
        assert client.limits == httpx.Limits(max_connections=1, max_keepalive_connections=1)
        assert client.proxy == "get_updates_proxy"
        assert client.http1 is True
        assert client.http2 is False
        assert media_write_timeout == [None, None]

    def test_custom_socket_options(self, builder, monkeypatch, bot):
        httpx_request_kwargs = []
        httpx_request_init = HTTPXRequest.__init__

        def init_transport(*args, **kwargs):
            nonlocal httpx_request_kwargs
            # This is called once for request and once for get_updates_request, so we make
            # it a list
            httpx_request_kwargs.append(kwargs.copy())
            httpx_request_init(*args, **kwargs)

        monkeypatch.setattr(HTTPXRequest, "__init__", init_transport)

        builder.token(bot.token).build()
        assert httpx_request_kwargs[0].get("socket_options") is None
        assert httpx_request_kwargs[1].get("socket_options") is None

        httpx_request_kwargs = []
        ApplicationBuilder().token(bot.token).socket_options(((1, 2, 3),)).connection_pool_size(
            "request"
        ).get_updates_socket_options(((4, 5, 6),)).get_updates_connection_pool_size(
            "get_updates"
        ).build()

        for kwargs in httpx_request_kwargs:
            if kwargs.get("connection_pool_size") == "request":
                assert kwargs.get("socket_options") == ((1, 2, 3),)
            else:
                assert kwargs.get("socket_options") == ((4, 5, 6),)

    def test_custom_application_class(self, bot, builder):
        class CustomApplication(Application):
            def __init__(self, arg, **kwargs):
                super().__init__(**kwargs)
                self.arg = arg

        builder.application_class(CustomApplication, kwargs={"arg": 2}).token(bot.token)

        app = builder.build()
        assert isinstance(app, CustomApplication)
        assert app.arg == 2

    @pytest.mark.parametrize(
        ("concurrent_updates", "expected"),
        [
            (4, SimpleUpdateProcessor(4)),
            (False, SimpleUpdateProcessor(1)),
            (True, SimpleUpdateProcessor(256)),
        ],
    )
    def test_all_application_args_custom(
        self, builder, bot, monkeypatch, concurrent_updates, expected
    ):
        job_queue = JobQueue()
        persistence = PicklePersistence("file_path")
        update_queue = asyncio.Queue()
        context_types = ContextTypes()

        async def post_init(app: Application) -> None:
            pass

        async def post_shutdown(app: Application) -> None:
            pass

        async def post_stop(app: Application) -> None:
            pass

        app = (
            builder.token(bot.token)
            .job_queue(job_queue)
            .persistence(persistence)
            .update_queue(update_queue)
            .context_types(context_types)
            .concurrent_updates(concurrent_updates)
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .post_stop(post_stop)
            .arbitrary_callback_data(True)
        ).build()

        assert app.job_queue is job_queue
        assert app.job_queue.application is app
        assert app.persistence is persistence
        assert app.persistence.bot is app.bot
        assert app.update_queue is update_queue
        assert app.updater.update_queue is update_queue
        assert app.updater.bot is app.bot
        assert app.context_types is context_types
        assert isinstance(app.update_processor, SimpleUpdateProcessor)
        assert app.update_processor.max_concurrent_updates == expected.max_concurrent_updates
        assert app.concurrent_updates == app.update_processor.max_concurrent_updates
        assert app.post_init is post_init
        assert app.post_shutdown is post_shutdown
        assert app.post_stop is post_stop
        assert isinstance(app.bot.callback_data_cache, CallbackDataCache)

        updater = Updater(bot=bot, update_queue=update_queue)
        app = ApplicationBuilder().updater(updater).build()
        assert app.updater is updater
        assert app.bot is updater.bot
        assert app.update_queue is updater.update_queue
        app = (
            builder.token(bot.token)
            .job_queue(job_queue)
            .persistence(persistence)
            .update_queue(update_queue)
            .context_types(context_types)
            .concurrent_updates(expected)
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .post_stop(post_stop)
            .arbitrary_callback_data(True)
        ).build()
        assert app.update_processor is expected

    @pytest.mark.parametrize("input_type", ["bytes", "str", "Path"])
    def test_all_private_key_input_types(self, builder, bot, input_type):
        private_key = data_file("private.key")
        password = data_file("private_key.password")

        if input_type == "bytes":
            private_key = private_key.read_bytes()
            password = password.read_bytes()
        if input_type == "str":
            private_key = str(private_key)
            password = str(password)

        builder.token(bot.token).private_key(
            private_key=private_key,
            password=password,
        )
        bot = builder.build().bot
        assert bot.private_key

    def test_no_updater(self, bot, builder):
        app = builder.token(bot.token).updater(None).build()
        assert app.bot.token == bot.token
        assert app.updater is None
        assert isinstance(app.update_queue, asyncio.Queue)
        assert isinstance(app.job_queue, JobQueue)
        assert app.job_queue.application is app

    @pytest.mark.filterwarnings("ignore::telegram.warnings.PTBUserWarning")
    def test_no_job_queue(self, bot, builder):
        app = builder.token(bot.token).job_queue(None).build()
        assert app.bot.token == bot.token
        assert app.job_queue is None
        assert isinstance(app.update_queue, asyncio.Queue)
        assert isinstance(app.updater, Updater)

    @pytest.mark.parametrize(
        ("read_timeout", "timeout", "expected"),
        [
            (None, None, 0),
            (1, None, 1),
            (None, 1, 1),
            (DEFAULT_NONE, None, 10),
            (DEFAULT_NONE, 1, 11),
            (1, 2, 3),
        ],
    )
    async def test_get_updates_read_timeout_value_passing(
        self, bot, read_timeout, timeout, expected, monkeypatch, builder
    ):
        # This test is a double check that ApplicationBuilder respects the changes of #3963 just
        # like `Bot` does - see also the corresponding test in test_bot.py (same name)
        caught_read_timeout = None

        async def catch_timeouts(*args, **kwargs):
            nonlocal caught_read_timeout
            caught_read_timeout = kwargs.get("read_timeout")
            return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        monkeypatch.setattr(HTTPXRequest, "do_request", catch_timeouts)

        bot = builder.get_updates_read_timeout(10).token(bot.token).build().bot
        await bot.get_updates(read_timeout=read_timeout, timeout=timeout)
        assert caught_read_timeout == expected
