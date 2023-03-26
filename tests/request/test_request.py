#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
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
"""Here we run tests directly with HTTPXRequest because that's easier than providing dummy
implementations for BaseRequest and we want to test HTTPXRequest anyway."""
import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Coroutine, Tuple

import httpx
import pytest

from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Conflict,
    Forbidden,
    InvalidToken,
    NetworkError,
    RetryAfter,
    TelegramError,
    TimedOut,
)
from telegram.request._httpxrequest import HTTPXRequest
from tests.auxil.envvars import TEST_WITH_OPT_DEPS
from tests.auxil.slots import mro_slots

# We only need mixed_rqs fixture, but it uses the others, so pytest needs us to import them as well
from .test_requestdata import (  # noqa: F401
    file_params,
    input_media_photo,
    input_media_video,
    inputfiles,
    mixed_params,
    mixed_rqs,
    simple_params,
)


def mocker_factory(
    response: bytes, return_code: int = HTTPStatus.OK
) -> Callable[[Tuple[Any]], Coroutine[Any, Any, Tuple[int, bytes]]]:
    async def make_assertion(*args, **kwargs):
        return return_code, response

    return make_assertion


@pytest.fixture()
async def httpx_request():
    async with HTTPXRequest() as rq:
        yield rq


@pytest.mark.skipif(
    TEST_WITH_OPT_DEPS, reason="Only relevant if the optional dependency is not installed"
)
class TestNoSocksHTTP2WithoutRequest:
    async def test_init(self, bot):
        with pytest.raises(RuntimeError, match=r"python-telegram-bot\[socks\]"):
            HTTPXRequest(proxy_url="socks5://foo")
        with pytest.raises(RuntimeError, match=r"python-telegram-bot\[http2\]"):
            HTTPXRequest(http_version="2")


@pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="Optional dependencies not installed")
class TestHTTP2WithRequest:
    async def test_http_2_response(self):
        httpx_request = HTTPXRequest(http_version="2")
        async with httpx_request:
            resp = await httpx_request._client.request(
                url="https://python-telegram-bot.org",
                method="GET",
                headers={"User-Agent": httpx_request.USER_AGENT},
            )
            assert resp.http_version == "HTTP/2"


# I picked not TEST_XXX because that's the default, meaning it will run by default for an end-user
# who runs pytest.
@pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="No need to run this twice")
class TestRequestWithoutRequest:
    test_flag = None

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = None

    async def test_init_import_errors(self, monkeypatch):
        """Makes sure that import errors are forwarded - related to TestNoSocks above"""

        def __init__(self, *args, **kwargs):
            raise ImportError("Other Error Message")

        monkeypatch.setattr(httpx.AsyncClient, "__init__", __init__)

        # Make sure that other exceptions are forwarded
        with pytest.raises(ImportError, match=r"Other Error Message"):
            HTTPXRequest(proxy_url="socks5://foo")

    def test_slot_behaviour(self):
        inst = HTTPXRequest()
        for attr in inst.__slots__:
            at = f"_{inst.__class__.__name__}{attr}" if attr.startswith("__") else attr
            assert getattr(inst, at, "err") != "err", f"got extra slot '{at}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    async def test_context_manager(self, monkeypatch):
        async def initialize():
            self.test_flag = ["initialize"]

        async def shutdown():
            self.test_flag.append("stop")

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, "initialize", initialize)
        monkeypatch.setattr(httpx_request, "shutdown", shutdown)

        async with httpx_request:
            pass

        assert self.test_flag == ["initialize", "stop"]

    async def test_context_manager_exception_on_init(self, monkeypatch):
        async def initialize():
            raise RuntimeError("initialize")

        async def shutdown():
            self.test_flag = "stop"

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, "initialize", initialize)
        monkeypatch.setattr(httpx_request, "shutdown", shutdown)

        with pytest.raises(RuntimeError, match="initialize"):
            async with httpx_request:
                pass

        assert self.test_flag == "stop"

    async def test_replaced_unprintable_char(self, monkeypatch, httpx_request):
        """Clients can send arbitrary bytes in callback data. Make sure that we just replace
        those
        """
        server_response = b'{"result": "test_string\x80"}'

        monkeypatch.setattr(httpx_request, "do_request", mocker_factory(response=server_response))

        assert await httpx_request.post(None, None, None) == "test_string�"
        # Explicitly call `parse_json_payload` here is well so that this public method is covered
        # not only implicitly.
        assert httpx_request.parse_json_payload(server_response) == {"result": "test_string�"}

    async def test_illegal_json_response(self, monkeypatch, httpx_request: HTTPXRequest):
        # for proper JSON it should be `"result":` instead of `result:`
        server_response = b'{result: "test_string"}'

        monkeypatch.setattr(httpx_request, "do_request", mocker_factory(response=server_response))

        with pytest.raises(TelegramError, match="Invalid server response"):
            await httpx_request.post(None, None, None)

    async def test_chat_migrated(self, monkeypatch, httpx_request: HTTPXRequest):
        server_response = b'{"ok": "False", "parameters": {"migrate_to_chat_id": 123}}'

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            mocker_factory(response=server_response, return_code=HTTPStatus.BAD_REQUEST),
        )

        with pytest.raises(ChatMigrated, match="New chat id: 123") as exc_info:
            await httpx_request.post(None, None, None)

        assert exc_info.value.new_chat_id == 123

    async def test_retry_after(self, monkeypatch, httpx_request: HTTPXRequest):
        server_response = b'{"ok": "False", "parameters": {"retry_after": 42}}'

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            mocker_factory(response=server_response, return_code=HTTPStatus.BAD_REQUEST),
        )

        with pytest.raises(RetryAfter, match="Retry in 42") as exc_info:
            await httpx_request.post(None, None, None)

        assert exc_info.value.retry_after == 42

    async def test_unknown_request_params(self, monkeypatch, httpx_request: HTTPXRequest):
        server_response = b'{"ok": "False", "parameters": {"unknown": "42"}}'

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            mocker_factory(response=server_response, return_code=HTTPStatus.BAD_REQUEST),
        )

        with pytest.raises(
            BadRequest,
            match="{'unknown': '42'}",
        ):
            await httpx_request.post(None, None, None)

    @pytest.mark.parametrize("description", [True, False])
    async def test_error_description(self, monkeypatch, httpx_request: HTTPXRequest, description):
        response_data = {"ok": "False"}
        if description:
            match = "ErrorDescription"
            response_data["description"] = match
        else:
            match = "Unknown HTTPError"

        server_response = json.dumps(response_data).encode("utf-8")

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            mocker_factory(response=server_response, return_code=-1),
        )

        with pytest.raises(NetworkError, match=match):
            await httpx_request.post(None, None, None)

        # Special casing for bad gateway
        if not description:
            monkeypatch.setattr(
                httpx_request,
                "do_request",
                mocker_factory(response=server_response, return_code=HTTPStatus.BAD_GATEWAY),
            )

            with pytest.raises(NetworkError, match="Bad Gateway"):
                await httpx_request.post(None, None, None)

    @pytest.mark.parametrize(
        ("code", "exception_class"),
        [
            (HTTPStatus.FORBIDDEN, Forbidden),
            (HTTPStatus.NOT_FOUND, InvalidToken),
            (HTTPStatus.UNAUTHORIZED, InvalidToken),
            (HTTPStatus.BAD_REQUEST, BadRequest),
            (HTTPStatus.CONFLICT, Conflict),
            (HTTPStatus.BAD_GATEWAY, NetworkError),
            (-1, NetworkError),
        ],
    )
    async def test_special_errors(
        self, monkeypatch, httpx_request: HTTPXRequest, code, exception_class
    ):
        server_response = b'{"ok": "False", "description": "Test Message"}'

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            mocker_factory(response=server_response, return_code=code),
        )

        with pytest.raises(exception_class, match="Test Message"):
            await httpx_request.post("", None, None)

    @pytest.mark.parametrize(
        ("exception", "catch_class", "match"),
        [
            (TelegramError("TelegramError"), TelegramError, "TelegramError"),
            (
                RuntimeError("CustomError"),
                Exception,
                r"HTTP implementation: RuntimeError\('CustomError'\)",
            ),
        ],
    )
    async def test_exceptions_in_do_request(
        self, monkeypatch, httpx_request: HTTPXRequest, exception, catch_class, match
    ):
        async def do_request(*args, **kwargs):
            raise exception

        monkeypatch.setattr(
            httpx_request,
            "do_request",
            do_request,
        )

        with pytest.raises(catch_class, match=match):
            await httpx_request.post(None, None, None)

    async def test_retrieve(self, monkeypatch, httpx_request):
        """Here we just test that retrieve gives us the raw bytes instead of trying to parse them
        as json
        """
        server_response = b'{"result": "test_string\x80"}'

        monkeypatch.setattr(httpx_request, "do_request", mocker_factory(response=server_response))

        assert await httpx_request.retrieve(None, None) == server_response

    async def test_timeout_propagation(self, monkeypatch, httpx_request):
        async def make_assertion(*args, **kwargs):
            self.test_flag = (
                kwargs.get("read_timeout"),
                kwargs.get("connect_timeout"),
                kwargs.get("write_timeout"),
                kwargs.get("pool_timeout"),
            )
            return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        monkeypatch.setattr(httpx_request, "do_request", make_assertion)

        await httpx_request.post("url", "method")
        assert self.test_flag == (DEFAULT_NONE, DEFAULT_NONE, DEFAULT_NONE, DEFAULT_NONE)

        await httpx_request.post(
            "url", None, read_timeout=1, connect_timeout=2, write_timeout=3, pool_timeout=4
        )
        assert self.test_flag == (1, 2, 3, 4)


@pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="No need to run this twice")
class TestHTTPXRequestWithoutRequest:
    test_flag = None

    @pytest.fixture(autouse=True)
    def _reset(self):
        self.test_flag = None

    def test_init(self, monkeypatch):
        @dataclass
        class Client:
            timeout: object
            proxies: object
            limits: object
            http1: object
            http2: object

        monkeypatch.setattr(httpx, "AsyncClient", Client)

        request = HTTPXRequest()
        assert request._client.timeout == httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=1.0)
        assert request._client.proxies is None
        assert request._client.limits == httpx.Limits(
            max_connections=1, max_keepalive_connections=1
        )
        assert request._client.http1 is True
        assert not request._client.http2

        request = HTTPXRequest(
            connection_pool_size=42,
            proxy_url="proxy_url",
            connect_timeout=43,
            read_timeout=44,
            write_timeout=45,
            pool_timeout=46,
        )
        assert request._client.proxies == "proxy_url"
        assert request._client.limits == httpx.Limits(
            max_connections=42, max_keepalive_connections=42
        )
        assert request._client.timeout == httpx.Timeout(connect=43, read=44, write=45, pool=46)

    async def test_multiple_inits_and_shutdowns(self, monkeypatch):
        self.test_flag = defaultdict(int)

        orig_init = httpx.AsyncClient.__init__
        orig_aclose = httpx.AsyncClient.aclose

        class Client(httpx.AsyncClient):
            def __init__(*args, **kwargs):
                orig_init(*args, **kwargs)
                self.test_flag["init"] += 1

            async def aclose(*args, **kwargs):
                await orig_aclose(*args, **kwargs)
                self.test_flag["shutdown"] += 1

        monkeypatch.setattr(httpx, "AsyncClient", Client)

        # Create a new one instead of using the fixture so that the mocking can work
        httpx_request = HTTPXRequest()

        await httpx_request.initialize()
        await httpx_request.initialize()
        await httpx_request.initialize()
        await httpx_request.shutdown()
        await httpx_request.shutdown()
        await httpx_request.shutdown()

        assert self.test_flag["init"] == 1
        assert self.test_flag["shutdown"] == 1

    async def test_multiple_init_cycles(self):
        # nothing really to assert - this should just not fail
        httpx_request = HTTPXRequest()
        async with httpx_request:
            await httpx_request.do_request(url="https://python-telegram-bot.org", method="GET")
        async with httpx_request:
            await httpx_request.do_request(url="https://python-telegram-bot.org", method="GET")

    async def test_http_version_error(self):
        with pytest.raises(ValueError, match="`http_version` must be either"):
            HTTPXRequest(http_version="1.0")

    async def test_http_1_response(self):
        httpx_request = HTTPXRequest(http_version="1.1")
        async with httpx_request:
            resp = await httpx_request._client.request(
                url="https://python-telegram-bot.org",
                method="GET",
                headers={"User-Agent": httpx_request.USER_AGENT},
            )
            assert resp.http_version == "HTTP/1.1"

    async def test_do_request_after_shutdown(self, httpx_request):
        await httpx_request.shutdown()
        with pytest.raises(RuntimeError, match="not initialized"):
            await httpx_request.do_request(url="url", method="GET")

    async def test_context_manager(self, monkeypatch):
        async def initialize():
            self.test_flag = ["initialize"]

        async def aclose(*args):
            self.test_flag.append("stop")

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, "initialize", initialize)
        monkeypatch.setattr(httpx.AsyncClient, "aclose", aclose)

        async with httpx_request:
            pass

        assert self.test_flag == ["initialize", "stop"]

    async def test_context_manager_exception_on_init(self, monkeypatch):
        async def initialize():
            raise RuntimeError("initialize")

        async def aclose(*args):
            self.test_flag = "stop"

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, "initialize", initialize)
        monkeypatch.setattr(httpx.AsyncClient, "aclose", aclose)

        with pytest.raises(RuntimeError, match="initialize"):
            async with httpx_request:
                pass

        assert self.test_flag == "stop"

    async def test_do_request_default_timeouts(self, monkeypatch):
        default_timeouts = httpx.Timeout(connect=42, read=43, write=44, pool=45)

        async def make_assertion(_, **kwargs):
            self.test_flag = kwargs.get("timeout") == default_timeouts
            return httpx.Response(HTTPStatus.OK)

        async with HTTPXRequest(
            connect_timeout=default_timeouts.connect,
            read_timeout=default_timeouts.read,
            write_timeout=default_timeouts.write,
            pool_timeout=default_timeouts.pool,
        ) as httpx_request:
            monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)
            await httpx_request.do_request(method="GET", url="URL")

        assert self.test_flag

    async def test_do_request_manual_timeouts(self, monkeypatch, httpx_request):
        default_timeouts = httpx.Timeout(connect=42, read=43, write=44, pool=45)
        manual_timeouts = httpx.Timeout(connect=52, read=53, write=54, pool=55)

        async def make_assertion(_, **kwargs):
            self.test_flag = kwargs.get("timeout") == manual_timeouts
            return httpx.Response(HTTPStatus.OK)

        async with HTTPXRequest(
            connect_timeout=default_timeouts.connect,
            read_timeout=default_timeouts.read,
            write_timeout=default_timeouts.write,
            pool_timeout=default_timeouts.pool,
        ) as httpx_request:
            monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)
            await httpx_request.do_request(
                method="GET",
                url="URL",
                connect_timeout=manual_timeouts.connect,
                read_timeout=manual_timeouts.read,
                write_timeout=manual_timeouts.write,
                pool_timeout=manual_timeouts.pool,
            )

        assert self.test_flag

    async def test_do_request_params_no_data(self, monkeypatch, httpx_request):
        async def make_assertion(self, **kwargs):
            method_assertion = kwargs.get("method") == "method"
            url_assertion = kwargs.get("url") == "url"
            files_assertion = kwargs.get("files") is None
            data_assertion = kwargs.get("data") is None
            if method_assertion and url_assertion and files_assertion and data_assertion:
                return httpx.Response(HTTPStatus.OK)
            return httpx.Response(HTTPStatus.BAD_REQUEST)

        monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)
        code, _ = await httpx_request.do_request(method="method", url="url")
        assert code == HTTPStatus.OK

    async def test_do_request_params_with_data(
        self, monkeypatch, httpx_request, mixed_rqs  # noqa: 9811
    ):
        async def make_assertion(self, **kwargs):
            method_assertion = kwargs.get("method") == "method"
            url_assertion = kwargs.get("url") == "url"
            files_assertion = kwargs.get("files") == mixed_rqs.multipart_data
            data_assertion = kwargs.get("data") == mixed_rqs.json_parameters
            if method_assertion and url_assertion and files_assertion and data_assertion:
                return httpx.Response(HTTPStatus.OK)
            return httpx.Response(HTTPStatus.BAD_REQUEST)

        monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)
        code, _ = await httpx_request.do_request(
            method="method",
            url="url",
            request_data=mixed_rqs,
        )
        assert code == HTTPStatus.OK

    async def test_do_request_return_value(self, monkeypatch, httpx_request):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            return httpx.Response(123, content=b"content")

        monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)
        code, content = await httpx_request.do_request(
            "method",
            "url",
        )
        assert code == 123
        assert content == b"content"

    @pytest.mark.parametrize(
        ("raised_class", "expected_class", "expected_message"),
        [
            (httpx.TimeoutException, TimedOut, "Timed out"),
            (httpx.ReadError, NetworkError, "httpx.ReadError: message"),
        ],
    )
    async def test_do_request_exceptions(
        self, monkeypatch, httpx_request, raised_class, expected_class, expected_message
    ):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            raise raised_class("message")

        monkeypatch.setattr(httpx.AsyncClient, "request", make_assertion)

        with pytest.raises(expected_class, match=expected_message):
            await httpx_request.do_request(
                "method",
                "url",
            )

    async def test_do_request_pool_timeout(self, monkeypatch):
        async def request(_, **kwargs):
            if self.test_flag is None:
                self.test_flag = True
            else:
                raise httpx.PoolTimeout("pool timeout")
            return httpx.Response(HTTPStatus.OK)

        monkeypatch.setattr(httpx.AsyncClient, "request", request)

        async with HTTPXRequest(pool_timeout=0.02) as httpx_request:
            with pytest.raises(TimedOut, match="Pool timeout"):
                await asyncio.gather(
                    httpx_request.do_request(method="GET", url="URL"),
                    httpx_request.do_request(method="GET", url="URL"),
                )


@pytest.mark.skipif(not TEST_WITH_OPT_DEPS, reason="No need to run this twice")
class TestHTTPXRequestWithRequest:
    async def test_do_request_wait_for_pool(self, httpx_request):
        """The pool logic is buried rather deeply in httpxcore, so we make actual requests here
        instead of mocking"""
        task_1 = asyncio.create_task(
            httpx_request.do_request(
                method="GET", url="https://python-telegram-bot.org/static/testfiles/telegram.mp4"
            )
        )
        task_2 = asyncio.create_task(
            httpx_request.do_request(
                method="GET", url="https://python-telegram-bot.org/static/testfiles/telegram.mp4"
            )
        )
        done, pending = await asyncio.wait({task_1, task_2}, return_when=asyncio.FIRST_COMPLETED)
        assert len(done) == len(pending) == 1
        done, pending = await asyncio.wait({task_1, task_2}, return_when=asyncio.ALL_COMPLETED)
        assert len(done) == 2
        assert len(pending) == 0
        try:  # retrieve exceptions from tasks
            task_1.exception()
            task_2.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            pass
