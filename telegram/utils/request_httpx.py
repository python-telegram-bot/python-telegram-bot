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
"""This module contains methods to make POST and GET requests using the httpx library."""
import logging
from typing import Tuple

import httpx

from .request import PtbRequestBase
from .types import JSONDict
from ..error import TimedOut, NetworkError


class PtbHttpx(PtbRequestBase):
    """Implementation of ``PtbRequestBase`` abstraction class using ``httpx`` async HTTP client.

    Args:
        con_pool_size (int): Number of connections to keep in the connection pool. (default: 1)
        proxy_url (str): The URL to the proxy server. For example: `http://127.0.0.1:3128`.
        connect_timeout (float): The maximum amount of time (in seconds) to wait for a
            connection attempt to a server to succeed. `None` will set an infinite timeout for
            connection attempts. (default: 5.0)
        read_timeout (float): The maximum amount of time (in seconds) to wait for a response from
            Telegram's server. `None` will set an infinite timeout. This value is usually
            overridden by the various ``telegram.Bot`` methods. (default: 5.0)
        write_timeout (float): The maximum amount of time (in seconds) to wait for a write
            operation to complete (in terms of a network socket; i.e. POSTing a request or
            uploading a file). `None` will set an infinite timeout. This value is usually
             overridden by the various ``telegram.Bot`` methods. (default: 5.0)
        pool_timeout (float): Timeout waiting for a connection object to become available and
            returned from the connection pool. `None` will set an infinite timeout. (default:
             no timeout)

    """

    def __init__(
        self,
        con_pool_size: int = 1,
        proxy_url: str = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 5.0,
        write_timeout: float = 5.0,
        pool_timeout: float = None,
    ):
        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout,
        )
        limits = httpx.Limits(
            max_connections=con_pool_size, max_keepalive_connections=con_pool_size
        )

        self._log = logging.getLogger(__name__)
        # TODO p0: Test client with proxy!
        self._client = httpx.AsyncClient(timeout=timeout, proxies=proxy_url, limits=limits)

    async def do_init(self) -> None:
        pass

    async def stop(self) -> None:
        await self._client.aclose()

    async def do_request(
        self,
        method: str,
        url: str,
        data: JSONDict,
        is_files: bool,
        read_timeout: float = None,
        write_timeout: float = None,
    ) -> Tuple[int, bytes]:
        timeout = self._client.timeout
        if read_timeout is not None:
            timeout.read = read_timeout
        if write_timeout is not None:
            timeout.write = write_timeout

        # TODO p0: On Linux, use setsockopt to properly set socket level keepalive.
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        #          (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 8)
        # TODO p4: Support setsockopt on lesser platforms than Linux.

        headers = {'User-Agent': self.user_agent}

        key = "data" if is_files else "json"
        kwargs = {key: data}

        try:
            res = await self._client.request(
                method, url, headers=headers, timeout=timeout, **kwargs
            )
        except httpx.TimeoutException as err:
            raise TimedOut() from err
        except httpx.HTTPError as err:
            # HTTPError must come last as its the base httpx exception class
            # TODO p4: do something smart here; for now just raise NetworkError
            raise NetworkError(f'httpx HTTPError {err}') from err

        return res.status_code, res.content
