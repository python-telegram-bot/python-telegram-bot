#
#  A library that provides a Python interface to the Telegram Bot API
#  Copyright (C) 2015-2022
#  Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser Public License for more details.
#
#  You should have received a copy of the GNU Lesser Public License
#  along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains methods to make POST and GET requests using the httpx library."""
import asyncio
import logging
from typing import Tuple, Optional

import httpx

from telegram._utils.defaultvalue import DefaultValue
from telegram._utils.types import ODVInput
from telegram.error import TimedOut, NetworkError
from telegram.request import BaseRequest, RequestData


# Note to future devs:
# Proxies are currently only tested manually. The httpx development docs have a nice guide on that:
# https://www.python-httpx.org/contributing/#development-proxy-setup (also saved on archive.org)
# That also works with socks5. Just pass `--mode socks5` to mitmproxy

_logger = logging.getLogger(__name__)


class HTTPXRequest(BaseRequest):
    """Implementation of :class:`~telegram.request.BaseRequest` using the library
    `httpx <https://www.python-httpx.org>`_.

    Args:
        connection_pool_size (:obj:`int`, optional): Number of connections to keep in the
            connection pool. Defaults to :obj:`1`.

            Note:
                Independent of the value, one additional connection will be reserved for
                :meth:`telegram.Bot.get_updates`.
        proxy_url (:obj:`str`, optional): The URL to the proxy server. For example
            ``'http://127.0.0.1:3128'`` or ``'socks5://127.0.0.1:3128'``. Defaults to :obj:`None`.

            Note:
                * The proxy URL can also be set via the environment variables ``HTTPS_PROXY`` or
                  ``ALL_PROXY``. See `the docs`_ of ``httpx`` for more info.
                * For Socks5 support, additional dependencies are required. Make sure to install
                  PTB via ``pip install python-telegram-bot[socks]`` in this case.
                * Socks5 proxies can not be set via environment variables.

            .. _the docs: https://www.python-httpx.org/environment_variables/#proxies
        connect_timeout (:obj:`float`, optional): The maximum amount of time (in seconds) to wait
            for a connection attempt to a server to succeed. :obj:`None` will set an infinite
            timeout for connection attempts. Defaults to ``5.0``.
        read_timeout (:obj:`float`, optional): The maximum amount of time (in seconds) to wait for
            a response from Telegram's server. :obj:`None` will set an infinite timeout. This value
            is usually overridden by the various methods of :class:`telegram.Bot`. Defaults to
            ``5.0``.
        write_timeout (:obj:`float`, optional): The maximum amount of time (in seconds) to wait for
            a write operation to complete (in terms of a network socket; i.e. POSTing a request or
            uploading a file).:obj:`None` will set an infinite timeout. Defaults to ``5.0``.
        pool_timeout (:obj:`float`, optional): The maximum amount of time (in seconds) to wait for
            a connection from the connection pool becoming available. :obj:`None` will set an
            infinite timeout. Defaults to :obj:`None`.

            Warning:
                With a finite pool timeout, you must expect :exc:`telegram.error.TimeOut`
                exceptions to be thrown when more requests are made simultaneously than there are
                connections in the connection pool!
    """

    __slots__ = ('_client', '__pool_semaphore')

    def __init__(
        self,
        connection_pool_size: int = 1,
        proxy_url: str = None,
        connect_timeout: Optional[float] = 5.0,
        read_timeout: Optional[float] = 5.0,
        write_timeout: Optional[float] = 5.0,
        pool_timeout: Optional[float] = 1.0,
    ):
        self.__pool_semaphore = asyncio.BoundedSemaphore(connection_pool_size)
        self._pool_timeout = pool_timeout

        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=1,
        )
        limits = httpx.Limits(
            max_connections=connection_pool_size,
            max_keepalive_connections=connection_pool_size,
        )

        self._client = httpx.AsyncClient(
            timeout=timeout,
            proxies=proxy_url,
            limits=limits,
        )

    async def initialize(self) -> None:
        """See :meth:`BaseRequest.initialize`."""

    async def shutdown(self) -> None:
        """See :meth:`BaseRequest.stop`."""
        await self._client.aclose()

    async def do_request(
        self,
        url: str,
        method: str,
        request_data: RequestData = None,
        connect_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        read_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        write_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        pool_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
    ) -> Tuple[int, bytes]:
        """See :meth:`BaseRequest.do_request`."""
        if isinstance(pool_timeout, DefaultValue):
            pool_timeout = self._pool_timeout

        if pool_timeout != 0 and self.__pool_semaphore.locked():
            _logger.debug(
                'All connections in the pool are currently busy. Waiting pool_timeout=%s for '
                'a connection to become available.',
                pool_timeout,
            )

        try:
            await asyncio.wait_for(self.__pool_semaphore.acquire(), timeout=pool_timeout)
        except asyncio.TimeoutError as exc:
            raise TimedOut('Pool timeout') from exc

        try:
            out = await self._do_request(
                url=url,
                method=method,
                request_data=request_data,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
            )
            return out
        finally:
            self.__pool_semaphore.release()

    async def _do_request(
        self,
        url: str,
        method: str,
        request_data: RequestData = None,
        connect_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        read_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
        write_timeout: ODVInput[float] = BaseRequest.DEFAULT_NONE,
    ) -> Tuple[int, bytes]:
        timeout = httpx.Timeout(
            connect=self._client.timeout.connect,
            read=self._client.timeout.read,
            write=self._client.timeout.write,
            pool=1,
        )
        if not isinstance(read_timeout, DefaultValue):
            timeout.read = read_timeout
        if not isinstance(write_timeout, DefaultValue):
            timeout.write = write_timeout
        if not isinstance(connect_timeout, DefaultValue):
            timeout.connect = connect_timeout

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
                headers={'User-Agent': self.USER_AGENT},
                timeout=timeout,
                files=files,
                data=data,
            )
        except httpx.TimeoutException as err:
            if isinstance(err, httpx.PoolTimeout):
                _logger.critical(
                    'All connections in the connection pool are occupied. Request was *not* sent '
                    'to Telegram. Adjust connection pool size!',
                )
                raise TimedOut('Pool timeout') from err
            raise TimedOut from err
        except httpx.HTTPError as err:
            # HTTPError must come last as its the base httpx exception class
            # TODO p4: do something smart here; for now just raise NetworkError
            raise NetworkError(f'httpx HTTPError: {err}') from err

        return res.status_code, res.content
