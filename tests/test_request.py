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
"""Here we run tests directly with HTTPXRequest because that's easier than providing dummy
implementations for BaseRequest and we want to test HTTPXRequest anyway."""
import json
from http import HTTPStatus
from typing import Tuple, Any, Coroutine, Callable

import httpx
import pytest

from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.error import (
    TelegramError,
    ChatMigrated,
    RetryAfter,
    NetworkError,
    Forbidden,
    InvalidToken,
    BadRequest,
    Conflict,
    TimedOut,
)
from telegram.request import BaseRequest, RequestData
from telegram.request._httpxrequest import HTTPXRequest

# We only need the first fixture, but it uses the others, so pytest needs us to import them as well
from .test_requestdata import (  # noqa: F401
    mixed_rqs,
    mixed_params,
    file_params,
    simple_params,
    inputfile,
    input_media_video,
    input_media_photo,
)


def mocker_factory(
    response: bytes, return_code: int = HTTPStatus.OK
) -> Callable[[Tuple[Any]], Coroutine[Any, Any, Tuple[int, bytes]]]:
    async def make_assertion(*args, **kwargs):
        return return_code, response

    return make_assertion


@pytest.fixture(scope='function')
@pytest.mark.asyncio
async def httpx_request():
    async with HTTPXRequest() as rq:
        yield rq


# TODO: Test timeouts


class TestRequest:
    test_flag = None

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = None

    def test_slot_behaviour(self, mro_slots):
        inst = HTTPXRequest()
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.mark.asyncio
    async def test_context_manager(self, monkeypatch):
        async def initialize():
            self.test_flag = ['initialize']

        async def stop():
            self.test_flag.append('stop')

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, 'initialize', initialize)
        monkeypatch.setattr(httpx_request, 'stop', stop)

        async with httpx_request:
            pass

        assert self.test_flag == ['initialize', 'stop']

    @pytest.mark.asyncio
    async def test_context_manager_exception_on_init(self, monkeypatch):
        async def initialize():
            raise RuntimeError('initialize')

        async def stop():
            self.test_flag = 'stop'

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, 'initialize', initialize)
        monkeypatch.setattr(httpx_request, 'stop', stop)

        with pytest.raises(RuntimeError, match='initialize'):
            async with httpx_request:
                pass

        assert self.test_flag == 'stop'

    @pytest.mark.asyncio
    async def test_replaced_unprintable_char(self, monkeypatch, httpx_request):
        """Clients can send arbitrary bytes in callback data. Make sure that we just replace
        those
        """
        server_response = b'{"result": "test_string\x80"}'

        monkeypatch.setattr(httpx_request, 'do_request', mocker_factory(response=server_response))

        assert await httpx_request.post(None, None, None) == 'test_string�'

    @pytest.mark.asyncio
    async def test_illegal_json_response(self, monkeypatch, httpx_request: HTTPXRequest):
        # for proper JSON it should be `"result":` instead of `result:`
        server_response = b'{result: "test_string"}'

        monkeypatch.setattr(httpx_request, 'do_request', mocker_factory(response=server_response))

        with pytest.raises(TelegramError, match='Invalid server response'):
            await httpx_request.post(None, None, None)

    @pytest.mark.asyncio
    async def test_chat_migrated(self, monkeypatch, httpx_request: HTTPXRequest):
        server_response = b'{"ok": "False", "parameters": {"migrate_to_chat_id": "123"}}'

        monkeypatch.setattr(
            httpx_request,
            'do_request',
            mocker_factory(response=server_response, return_code=HTTPStatus.BAD_REQUEST),
        )

        with pytest.raises(ChatMigrated, match='New chat id: 123') as exc_info:
            await httpx_request.post(None, None, None)

        assert exc_info.value.new_chat_id == 123

    @pytest.mark.asyncio
    async def test_retry_after(self, monkeypatch, httpx_request: HTTPXRequest):
        server_response = b'{"ok": "False", "parameters": {"retry_after": "42"}}'

        monkeypatch.setattr(
            httpx_request,
            'do_request',
            mocker_factory(response=server_response, return_code=HTTPStatus.BAD_REQUEST),
        )

        with pytest.raises(RetryAfter, match='Retry in 42.0') as exc_info:
            await httpx_request.post(None, None, None)

        assert exc_info.value.retry_after == 42.0

    @pytest.mark.asyncio
    @pytest.mark.parametrize('description', [True, False])
    async def test_error_description(self, monkeypatch, httpx_request: HTTPXRequest, description):
        response_data = {"ok": "False"}
        if description:
            match = 'ErrorDescription'
            response_data['description'] = match
        else:
            match = 'Unknown HTTPError'

        server_response = json.dumps(response_data).encode('utf-8')

        monkeypatch.setattr(
            httpx_request,
            'do_request',
            mocker_factory(response=server_response, return_code=-1),
        )

        with pytest.raises(NetworkError, match=match):
            await httpx_request.post(None, None, None)

        # Special casing for bad gateway
        if not description:
            monkeypatch.setattr(
                httpx_request,
                'do_request',
                mocker_factory(response=server_response, return_code=HTTPStatus.BAD_GATEWAY),
            )

            with pytest.raises(NetworkError, match='Bad Gateway'):
                await httpx_request.post(None, None, None)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'code, exception_class',
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
            'do_request',
            mocker_factory(response=server_response, return_code=code),
        )

        with pytest.raises(exception_class, match='Test Message'):
            await httpx_request.post(None, None, None)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ['exception', 'catch_class', 'match'],
        [
            (TelegramError('TelegramError'), TelegramError, 'TelegramError'),
            (RuntimeError('CustomError'), Exception, 'HTTP implementation: CustomError'),
        ],
    )
    async def test_exceptions_in_do_request(
        self, monkeypatch, httpx_request: HTTPXRequest, exception, catch_class, match
    ):
        async def do_request(*args, **kwargs):
            raise exception

        monkeypatch.setattr(
            httpx_request,
            'do_request',
            do_request,
        )

        with pytest.raises(catch_class, match=match):
            await httpx_request.post(None, None, None)

    @pytest.mark.asyncio
    async def test_retrieve(self, monkeypatch, httpx_request):
        """Here we just test that retrieve gives us the raw bytes instead of trying to parse them
        as json
        """
        server_response = b'{"result": "test_string\x80"}'

        monkeypatch.setattr(httpx_request, 'do_request', mocker_factory(response=server_response))

        assert await httpx_request.retrieve(None, None) == server_response

    def test_connection_pool_size(self):
        class Request(BaseRequest):
            async def do_request(self, *args, **kwargs):
                pass

            async def initialize(self, *args, **kwargs):
                pass

            async def shutdown(self, *args, **kwargs):
                pass

        with pytest.raises(NotImplementedError):
            Request().connection_pool_size

    @pytest.mark.asyncio
    async def test_timeout_propagation(self, monkeypatch, httpx_request):
        """Here we just test that retrieve gives us the raw bytes instead of trying to parse them
        as json
        """

        async def make_assertion(
            method: str,
            url: str,
            request_data: RequestData = None,
            read_timeout: ODVInput[float] = DEFAULT_NONE,
            *args,
            **kwargs,
        ):
            self.test_flag = read_timeout
            return HTTPStatus.OK, b'{"ok": "True", "result": {}}'

        monkeypatch.setattr(httpx_request, 'do_request', make_assertion)

        await httpx_request.post('url', None, read_timeout=42.314)
        assert self.test_flag == 42.314


class TestHTTPXRequest:
    test_flag = None

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = None

    def test_init(self):
        request = HTTPXRequest()
        assert request.connection_pool_size == 1
        assert request._client.timeout == httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=1.0)

        request = HTTPXRequest(
            connection_pool_size=42,
            connect_timeout=43,
            read_timeout=44,
            write_timeout=45,
            pool_timeout=46,
        )
        assert request.connection_pool_size == 42
        assert request._client.timeout == httpx.Timeout(connect=43, read=44, write=45, pool=46)

    @pytest.mark.asyncio
    async def test_context_manager(self, monkeypatch):
        async def initialize():
            self.test_flag = ['initialize']

        async def aclose(*args):
            self.test_flag.append('stop')

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, 'initialize', initialize)
        monkeypatch.setattr(httpx.AsyncClient, 'aclose', aclose)

        async with httpx_request:
            pass

        assert self.test_flag == ['initialize', 'stop']

    @pytest.mark.asyncio
    async def test_context_manager_exception_on_init(self, monkeypatch):
        async def initialize():
            raise RuntimeError('initialize')

        async def aclose(*args):
            self.test_flag = 'stop'

        httpx_request = HTTPXRequest()

        monkeypatch.setattr(httpx_request, 'initialize', initialize)
        monkeypatch.setattr(httpx.AsyncClient, 'aclose', aclose)

        with pytest.raises(RuntimeError, match='initialize'):
            async with httpx_request:
                pass

        assert self.test_flag == 'stop'

    @pytest.mark.asyncio
    async def test_do_request_default_timeouts(self, monkeypatch, httpx_request):
        default_timeouts = httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=1.0)

        async def make_assertion(self, method, url, headers, timeout, files, data):
            self.test_flag = timeout == default_timeouts
            return httpx.Response(HTTPStatus.OK)

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)
        await httpx_request.do_request('GET', 'URL')
        assert httpx_request._client.timeout == default_timeouts

    @pytest.mark.asyncio
    async def test_do_request_manual_timeouts(self, monkeypatch, httpx_request):
        default_timeouts = httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=1.0)

        async def make_assertion(self, method, url, headers, timeout, files, data):
            self.test_flag = timeout == httpx.Timeout(connect=5.0, read=5.5, write=5.6, pool=1.0)
            return httpx.Response(HTTPStatus.OK)

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)
        await httpx_request.do_request('GET', 'URL', read_timeout=5.5, write_timeout=5.6)
        assert httpx_request._client.timeout == default_timeouts

    @pytest.mark.asyncio
    async def test_do_request_params_no_data(self, monkeypatch, httpx_request):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            method_assertion = method == 'method'
            url_assertion = url == 'url'
            files_assertion = files is None
            data_assertion = data is None
            if method_assertion and url_assertion and files_assertion and data_assertion:
                return httpx.Response(HTTPStatus.OK)
            return httpx.Response(HTTPStatus.BAD_REQUEST)

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)
        code, _ = await httpx_request.do_request(
            'method', 'url', read_timeout=5.5, write_timeout=5.6
        )
        assert code == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_do_request_params_with_data(
        self, monkeypatch, httpx_request, mixed_rqs  # noqa: 9811
    ):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            method_assertion = method == 'method'
            url_assertion = url == 'url'
            files_assertion = files == mixed_rqs.multipart_data
            data_assertion = data == mixed_rqs.json_parameters
            if method_assertion and url_assertion and files_assertion and data_assertion:
                return httpx.Response(HTTPStatus.OK)
            return httpx.Response(HTTPStatus.BAD_REQUEST)

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)
        code, _ = await httpx_request.do_request(
            'method',
            'url',
            read_timeout=5.5,
            write_timeout=5.6,
            request_data=mixed_rqs,
        )
        assert code == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_do_request_return_value(self, monkeypatch, httpx_request):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            return httpx.Response(123, content=b'content')

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)
        code, content = await httpx_request.do_request(
            'method',
            'url',
        )
        assert code == 123
        assert content == b'content'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ['raised_class', 'expected_class'],
        [(httpx.TimeoutException, TimedOut), (httpx.HTTPError, NetworkError)],
    )
    async def test_do_request_exceptions(
        self, monkeypatch, httpx_request, raised_class, expected_class
    ):
        async def make_assertion(self, method, url, headers, timeout, files, data):
            raise raised_class('message')

        monkeypatch.setattr(httpx.AsyncClient, 'request', make_assertion)

        with pytest.raises(expected_class):
            await httpx_request.do_request(
                'method',
                'url',
            )
