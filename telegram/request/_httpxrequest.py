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
"""This module contains methods to make POST and GET requests using the httpx library."""
from typing import Optional, Tuple

import httpx

from telegram._utils.defaultvalue import DefaultValue
from telegram._utils.logging import get_logger
from telegram._utils.types import ODVInput
from telegram.error import NetworkError, TimedOut
from telegram.request._baserequest import BaseRequest
from telegram.request._requestdata import RequestData

# Note to future devs:
# Proxies are currently only tested manually. The httpx development docs have a nice guide on that:
# https://www.python-httpx.org/contributing/#development-proxy-setup (also saved on archive.org)
# That also works with socks5. Just pass `--mode socks5` to mitmproxy

_LOGGER = get_logger(__name__, "HTTPXRequest")


class HTTPXRequest(BaseRequest):
    """Implementation of :class:`~telegram.request.BaseRequest` using the library
    `httpx <https://www.python-httpx.org>`_.

    .. versionadded:: 20.0

    Args:
        connection_pool_size (:obj:`int`, optional): Number of connections to keep in the
            connection pool. Defaults to ``1``.

            Note:
                Independent of the value, one additional connection will be reserved for
                :meth:`telegram.Bot.get_updates`.
        proxy_url (:obj:`str`, optional): The URL to the proxy server. For example
            ``'http://127.0.0.1:3128'`` or ``'socks5://127.0.0.1:3128'``. Defaults to :obj:`None`.

            Note:
                * The proxy URL can also be set via the environment variables ``HTTPS_PROXY`` or
                  ``ALL_PROXY``. See `the docs of httpx`_ for more info.
                * For Socks5 support, additional dependencies are required. Make sure to install
                  PTB via :command:`pip install python-telegram-bot[socks]` in this case.
                * Socks5 proxies can not be set via environment variables.

            .. _the docs of httpx: https://www.python-httpx.org/environment_variables/#proxies
        read_timeout (:obj:`float` | :obj:`None`, optional): If passed, specifies the maximum
            amount of time (in seconds) to wait for a response from Telegram's server.
            This value is used unless a different value is passed to :meth:`do_request`.
            Defaults to ``5``.
        write_timeout (:obj:`float` | :obj:`None`, optional): If passed, specifies the maximum
            amount of time (in seconds) to wait for a write operation to complete (in terms of
            a network socket; i.e. POSTing a request or uploading a file).
            This value is used unless a different value is passed to :meth:`do_request`.
            Defaults to ``5``.
        connect_timeout (:obj:`float` | :obj:`None`, optional): If passed, specifies the
            maximum amount of time (in seconds) to wait for a connection attempt to a server
            to succeed. This value is used unless a different value is passed to
            :meth:`do_request`. Defaults to ``5``.
        pool_timeout (:obj:`float` | :obj:`None`, optional): If passed, specifies the maximum
            amount of time (in seconds) to wait for a connection to become available.
            This value is used unless a different value is passed to :meth:`do_request`.
            Defaults to ``1``.

            Warning:
                With a finite pool timeout, you must expect :exc:`telegram.error.TimedOut`
                exceptions to be thrown when more requests are made simultaneously than there are
                connections in the connection pool!
        http_version (:obj:`str`, optional): If ``"2"``, HTTP/2 will be used instead of HTTP/1.1.
            Defaults to ``"1.1"``.

            .. versionadded:: 20.1
            .. versionchanged:: 20.2
                Reset the default version to 1.1.

    """

    __slots__ = ("_client", "_client_kwargs", "_http_version")

    def __init__(
        self,
        connection_pool_size: int = 1,
        proxy_url: str = None,
        read_timeout: Optional[float] = 5.0,
        write_timeout: Optional[float] = 5.0,
        connect_timeout: Optional[float] = 5.0,
        pool_timeout: Optional[float] = 1.0,
        http_version: str = "1.1",
    ):
        self._http_version = http_version
        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout,
        )
        limits = httpx.Limits(
            max_connections=connection_pool_size,
            max_keepalive_connections=connection_pool_size,
        )

        if http_version not in ("1.1", "2"):
            raise ValueError("`http_version` must be either '1.1' or '2'.")

        http1 = http_version == "1.1"

        # See https://github.com/python-telegram-bot/python-telegram-bot/pull/3542
        # for why we need to use `dict()` here.
        self._client_kwargs = dict(  # pylint: disable=use-dict-literal  # noqa: C408
            timeout=timeout,
            proxies=proxy_url,
            limits=limits,
            http1=http1,
            http2=not http1,
        )

        try:
            self._client = self._build_client()
        except ImportError as exc:
            if "httpx[http2]" not in str(exc) and "httpx[socks]" not in str(exc):
                raise exc

            if "httpx[socks]" in str(exc):
                raise RuntimeError(
                    "To use Socks5 proxies, PTB must be installed via `pip install "
                    "python-telegram-bot[socks]`."
                ) from exc
            raise RuntimeError(
                "To use HTTP/2, PTB must be installed via `pip install "
                "python-telegram-bot[http2]`."
            ) from exc

    @property
    def http_version(self) -> str:
        """
        :obj:`str`: Used HTTP version, see :paramref:`http_version`.

        .. versionadded:: 20.2
        """
        return self._http_version

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(**self._client_kwargs)  # type: ignore[arg-type]

    async def initialize(self) -> None:
        """See :meth:`BaseRequest.initialize`."""
        if self._client.is_closed:
            self._client = self._build_client()

    async def shutdown(self) -> None:
        """See :meth:`BaseRequest.shutdown`."""
        if self._client.is_closed:
            _LOGGER.debug("This HTTPXRequest is already shut down. Returning.")
            return

        await self._client.aclose()

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: RequestData = None,
        read_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        write_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        connect_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        pool_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
    ) -> Tuple[int, bytes]:
        """See :meth:`BaseRequest.do_request`."""
        if self._client.is_closed:
            raise RuntimeError("This HTTPXRequest is not initialized!")

        # If user did not specify timeouts (for e.g. in a bot method), use the default ones when we
        # created this instance.
        if isinstance(read_timeout, DefaultValue):
            read_timeout = self._client.timeout.read
        if isinstance(write_timeout, DefaultValue):
            write_timeout = self._client.timeout.write
        if isinstance(connect_timeout, DefaultValue):
            connect_timeout = self._client.timeout.connect
        if isinstance(pool_timeout, DefaultValue):
            pool_timeout = self._client.timeout.pool

        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout,
        )

        # TODO p0: On Linux, use setsockopt to properly set socket level keepalive.
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 8)
        # TODO p4: Support setsockopt on lesser platforms than Linux.

        files = request_data.multipart_data if request_data else None
        data = request_data.json_parameters if request_data else None

        try:
            res = await self._client.request(
                method=method,
                url=url,
                headers={"User-Agent": self.USER_AGENT},
                timeout=timeout,
                files=files,
                data=data,
            )
        except httpx.TimeoutException as err:
            if isinstance(err, httpx.PoolTimeout):
                raise TimedOut(
                    message=(
                        "Pool timeout: All connections in the connection pool are occupied. "
                        "Request was *not* sent to Telegram. Consider adjusting the connection "
                        "pool size or the pool timeout."
                    )
                ) from err
            raise TimedOut from err
        except httpx.HTTPError as err:
            # HTTPError must come last as its the base httpx exception class
            # TODO p4: do something smart here; for now just raise NetworkError

            # We include the class name for easier debugging. Especially useful if the error
            # message of `err` is empty.
            raise NetworkError(f"httpx.{err.__class__.__name__}: {err}") from err

        return res.status_code, res.content
