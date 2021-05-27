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
"""This module contains methods to make POST and GET requests."""
import logging
import os
import socket
import sys
import warnings

try:
    import ujson as json
except ImportError:
    import json  # type: ignore[no-redef]

from typing import Any, Union

import certifi

try:
    import telegram.vendor.ptb_urllib3.urllib3 as urllib3
    import telegram.vendor.ptb_urllib3.urllib3.contrib.appengine as appengine
    from telegram.vendor.ptb_urllib3.urllib3.connection import HTTPConnection
    from telegram.vendor.ptb_urllib3.urllib3.fields import RequestField
    from telegram.vendor.ptb_urllib3.urllib3.util.timeout import Timeout
except ImportError:  # pragma: no cover
    try:
        import urllib3  # type: ignore[no-redef]
        import urllib3.contrib.appengine as appengine  # type: ignore[no-redef]
        from urllib3.connection import HTTPConnection  # type: ignore[no-redef]
        from urllib3.fields import RequestField  # type: ignore[no-redef]
        from urllib3.util.timeout import Timeout  # type: ignore[no-redef]

        warnings.warn(
            'python-telegram-bot is using upstream urllib3. This is allowed but not '
            'supported by python-telegram-bot maintainers.'
        )
    except ImportError:
        warnings.warn(
            "python-telegram-bot wasn't properly installed. Please refer to README.rst on "
            "how to properly install."
        )
        raise

# pylint: disable=C0412
from telegram import InputFile, InputMedia, TelegramError
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Conflict,
    InvalidToken,
    NetworkError,
    RetryAfter,
    TimedOut,
    Unauthorized,
)
from telegram.utils.types import JSONDict
from telegram.utils.deprecate import set_new_attribute_deprecated


def _render_part(self: RequestField, name: str, value: str) -> str:  # pylint: disable=W0613
    r"""
    Monkey patch urllib3.urllib3.fields.RequestField to make it *not* support RFC2231 compliant
    Content-Disposition headers since telegram servers don't understand it. Instead just escape
    \\ and " and replace any \n and \r with a space.
    """
    value = value.replace('\\', '\\\\').replace('"', '\\"')
    value = value.replace('\r', ' ').replace('\n', ' ')
    return f'{name}="{value}"'


RequestField._render_part = _render_part  # type: ignore  # pylint: disable=W0212

logging.getLogger('telegram.vendor.ptb_urllib3.urllib3').setLevel(logging.WARNING)

USER_AGENT = 'Python Telegram Bot (https://github.com/python-telegram-bot/python-telegram-bot)'


class Request:
    """
    Helper class for python-telegram-bot which provides methods to perform POST & GET towards
    Telegram servers.

    Args:
        con_pool_size (:obj:`int`): Number of connections to keep in the connection pool.
        proxy_url (:obj:`str`): The URL to the proxy server. For example: `http://127.0.0.1:3128`.
        urllib3_proxy_kwargs (:obj:`dict`): Arbitrary arguments passed as-is to
            :obj:`urllib3.ProxyManager`. This value will be ignored if :attr:`proxy_url` is not
            set.
        connect_timeout (:obj:`int` | :obj:`float`): The maximum amount of time (in seconds) to
            wait for a connection attempt to a server to succeed. :obj:`None` will set an
            infinite timeout for connection attempts. Defaults to ``5.0``.
        read_timeout (:obj:`int` | :obj:`float`): The maximum amount of time (in seconds) to wait
            between consecutive read operations for a response from the server. :obj:`None` will
            set an infinite timeout. This value is usually overridden by the various
            :class:`telegram.Bot` methods. Defaults to ``5.0``.

    """

    __slots__ = ('_connect_timeout', '_con_pool_size', '_con_pool', '__dict__')

    def __init__(
        self,
        con_pool_size: int = 1,
        proxy_url: str = None,
        urllib3_proxy_kwargs: JSONDict = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 5.0,
    ):
        if urllib3_proxy_kwargs is None:
            urllib3_proxy_kwargs = {}

        self._connect_timeout = connect_timeout

        sockopts = HTTPConnection.default_socket_options + [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        ]

        # TODO: Support other platforms like mac and windows.
        if 'linux' in sys.platform:
            sockopts.append(
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 120)  # pylint: disable=no-member
            )
            sockopts.append(
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)  # pylint: disable=no-member
            )
            sockopts.append(
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 8)  # pylint: disable=no-member
            )

        self._con_pool_size = con_pool_size

        kwargs = dict(
            maxsize=con_pool_size,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            socket_options=sockopts,
            timeout=urllib3.Timeout(connect=self._connect_timeout, read=read_timeout, total=None),
        )

        # Set a proxy according to the following order:
        # * proxy defined in proxy_url (+ urllib3_proxy_kwargs)
        # * proxy set in `HTTPS_PROXY` env. var.
        # * proxy set in `https_proxy` env. var.
        # * None (if no proxy is configured)

        if not proxy_url:
            proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        self._con_pool: Union[
            urllib3.PoolManager,
            appengine.AppEngineManager,
            'SOCKSProxyManager',  # noqa: F821
            urllib3.ProxyManager,
        ] = None  # type: ignore
        if not proxy_url:
            if appengine.is_appengine_sandbox():
                # Use URLFetch service if running in App Engine
                self._con_pool = appengine.AppEngineManager()
            else:
                self._con_pool = urllib3.PoolManager(**kwargs)
        else:
            kwargs.update(urllib3_proxy_kwargs)
            if proxy_url.startswith('socks'):
                try:
                    # pylint: disable=C0415
                    from telegram.vendor.ptb_urllib3.urllib3.contrib.socks import SOCKSProxyManager
                except ImportError as exc:
                    raise RuntimeError('PySocks is missing') from exc
                self._con_pool = SOCKSProxyManager(proxy_url, **kwargs)
            else:
                mgr = urllib3.proxy_from_url(proxy_url, **kwargs)
                if mgr.proxy.auth:
                    # TODO: what about other auth types?
                    auth_hdrs = urllib3.make_headers(proxy_basic_auth=mgr.proxy.auth)
                    mgr.proxy_headers.update(auth_hdrs)

                self._con_pool = mgr

    def __setattr__(self, key: str, value: object) -> None:
        set_new_attribute_deprecated(self, key, value)

    @property
    def con_pool_size(self) -> int:
        """The size of the connection pool used."""
        return self._con_pool_size

    def stop(self) -> None:
        """Performs cleanup on shutdown."""
        self._con_pool.clear()  # type: ignore

    @staticmethod
    def _parse(json_data: bytes) -> Union[JSONDict, bool]:
        """Try and parse the JSON returned from Telegram.

        Returns:
            dict: A JSON parsed as Python dict with results - on error this dict will be empty.

        """
        decoded_s = json_data.decode('utf-8', 'replace')
        try:
            data = json.loads(decoded_s)
        except ValueError as exc:
            raise TelegramError('Invalid server response') from exc

        if not data.get('ok'):  # pragma: no cover
            description = data.get('description')
            parameters = data.get('parameters')
            if parameters:
                migrate_to_chat_id = parameters.get('migrate_to_chat_id')
                if migrate_to_chat_id:
                    raise ChatMigrated(migrate_to_chat_id)
                retry_after = parameters.get('retry_after')
                if retry_after:
                    raise RetryAfter(retry_after)
            if description:
                return description

        return data['result']

    def _request_wrapper(self, *args: object, **kwargs: Any) -> bytes:
        """Wraps urllib3 request for handling known exceptions.

        Args:
            args: unnamed arguments, passed to urllib3 request.
            kwargs: keyword arguments, passed to urllib3 request.

        Returns:
            bytes: A non-parsed JSON text.

        Raises:
            TelegramError

        """
        # Make sure to hint Telegram servers that we reuse connections by sending
        # "Connection: keep-alive" in the HTTP headers.
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['connection'] = 'keep-alive'
        # Also set our user agent
        kwargs['headers']['user-agent'] = USER_AGENT

        try:
            resp = self._con_pool.request(*args, **kwargs)
        except urllib3.exceptions.TimeoutError as error:
            raise TimedOut() from error
        except urllib3.exceptions.HTTPError as error:
            # HTTPError must come last as its the base urllib3 exception class
            # TODO: do something smart here; for now just raise NetworkError
            raise NetworkError(f'urllib3 HTTPError {error}') from error

        if 200 <= resp.status <= 299:
            # 200-299 range are HTTP success statuses
            return resp.data

        try:
            message = str(self._parse(resp.data))
        except ValueError:
            message = 'Unknown HTTPError'

        if resp.status in (401, 403):
            raise Unauthorized(message)
        if resp.status == 400:
            raise BadRequest(message)
        if resp.status == 404:
            raise InvalidToken()
        if resp.status == 409:
            raise Conflict(message)
        if resp.status == 413:
            raise NetworkError(
                'File too large. Check telegram api limits '
                'https://core.telegram.org/bots/api#senddocument'
            )
        if resp.status == 502:
            raise NetworkError('Bad Gateway')
        raise NetworkError(f'{message} ({resp.status})')

    def post(self, url: str, data: JSONDict, timeout: float = None) -> Union[JSONDict, bool]:
        """Request an URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            data (Dict[:obj:`str`, :obj:`str` | :obj:`int`], optional): A dict of key/value pairs.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
          A JSON object.

        """
        urlopen_kwargs = {}

        if timeout is not None:
            urlopen_kwargs['timeout'] = Timeout(read=timeout, connect=self._connect_timeout)

        if data is None:
            data = {}

        # Are we uploading files?
        files = False

        # pylint: disable=R1702
        for key, val in data.copy().items():
            if isinstance(val, InputFile):
                # Convert the InputFile to urllib3 field format
                data[key] = val.field_tuple
                files = True
            elif isinstance(val, (float, int)):
                # Urllib3 doesn't like floats it seems
                data[key] = str(val)
            elif key == 'media':
                # One media or multiple
                if isinstance(val, InputMedia):
                    # Attach and set val to attached name
                    data[key] = val.to_json()
                    if isinstance(val.media, InputFile):  # type: ignore
                        data[val.media.attach] = val.media.field_tuple  # type: ignore
                else:
                    # Attach and set val to attached name for all
                    media = []
                    for med in val:
                        media_dict = med.to_dict()
                        media.append(media_dict)
                        if isinstance(med.media, InputFile):
                            data[med.media.attach] = med.media.field_tuple
                            # if the file has a thumb, we also need to attach it to the data
                            if "thumb" in media_dict:
                                data[med.thumb.attach] = med.thumb.field_tuple
                    data[key] = json.dumps(media)
                files = True
            elif isinstance(val, list):
                # In case we're sending files, we need to json-dump lists manually
                # As we can't know if that's the case, we just json-dump here
                data[key] = json.dumps(val)

        # Use multipart upload if we're uploading files, otherwise use JSON
        if files:
            result = self._request_wrapper('POST', url, fields=data, **urlopen_kwargs)
        else:
            result = self._request_wrapper(
                'POST',
                url,
                body=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                **urlopen_kwargs,
            )

        return self._parse(result)

    def retrieve(self, url: str, timeout: float = None) -> bytes:
        """Retrieve the contents of a file by its URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            timeout (:obj:`int` | :obj:`float`): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        """
        urlopen_kwargs = {}
        if timeout is not None:
            urlopen_kwargs['timeout'] = Timeout(read=timeout, connect=self._connect_timeout)

        return self._request_wrapper('GET', url, **urlopen_kwargs)

    def download(self, url: str, filename: str, timeout: float = None) -> None:
        """Download a file by its URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            filename (:obj:`str`): The filename within the path to download the file.

        """
        buf = self.retrieve(url, timeout=timeout)
        with open(filename, 'wb') as fobj:
            fobj.write(buf)
