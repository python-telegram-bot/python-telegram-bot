#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
from builtins import str  # For PY2

try:
    import ujson as json
except ImportError:
    import json

import certifi

try:
    import telegram.vendor.ptb_urllib3.urllib3 as urllib3
    import telegram.vendor.ptb_urllib3.urllib3.contrib.appengine as appengine
    from telegram.vendor.ptb_urllib3.urllib3.connection import HTTPConnection
    from telegram.vendor.ptb_urllib3.urllib3.util.timeout import Timeout
    from telegram.vendor.ptb_urllib3.urllib3.fields import RequestField
except ImportError:  # pragma: no cover
    warnings.warn("python-telegram-bot wasn't properly installed. Please refer to README.rst on "
                  "how to properly install.")
    raise

from telegram import (InputFile, TelegramError, InputMedia)
from telegram.error import (Unauthorized, NetworkError, TimedOut, BadRequest, ChatMigrated,
                            RetryAfter, InvalidToken, Conflict)


def _render_part(self, name, value):
    """
    Monkey patch urllib3.urllib3.fields.RequestField to make it *not* support RFC2231 compliant
    Content-Disposition headers since telegram servers don't understand it. Instead just escape
    \ and " and replace any \n and \r with a space.
    """
    value = value.replace(u'\\', u'\\\\').replace(u'"', u'\\"')
    value = value.replace(u'\r', u' ').replace(u'\n', u' ')
    return u'%s="%s"' % (name, value)


RequestField._render_part = _render_part

logging.getLogger('urllib3').setLevel(logging.WARNING)

USER_AGENT = 'Python Telegram Bot (https://github.com/python-telegram-bot/python-telegram-bot)'


class Request(object):
    """
    Helper class for python-telegram-bot which provides methods to perform POST & GET towards
    telegram servers.

    Args:
        con_pool_size (int): Number of connections to keep in the connection pool.
        proxy_url (str): The URL to the proxy server. For example: `http://127.0.0.1:3128`.
        urllib3_proxy_kwargs (dict): Arbitrary arguments passed as-is to `urllib3.ProxyManager`.
            This value will be ignored if proxy_url is not set.
        connect_timeout (int|float): The maximum amount of time (in seconds) to wait for a
            connection attempt to a server to succeed. None will set an infinite timeout for
            connection attempts. (default: 5.)
        read_timeout (int|float): The maximum amount of time (in seconds) to wait between
            consecutive read operations for a response from the server. None will set an infinite
            timeout. This value is usually overridden by the various ``telegram.Bot`` methods.
            (default: 5.)

    """

    def __init__(self,
                 con_pool_size=1,
                 proxy_url=None,
                 urllib3_proxy_kwargs=None,
                 connect_timeout=5.,
                 read_timeout=5.):
        if urllib3_proxy_kwargs is None:
            urllib3_proxy_kwargs = dict()

        self._connect_timeout = connect_timeout

        sockopts = HTTPConnection.default_socket_options + [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)]

        # TODO: Support other platforms like mac and windows.
        if 'linux' in sys.platform:
            sockopts.append((socket.IPPROTO_TCP,
                             socket.TCP_KEEPIDLE, 120))  # pylint: disable=no-member
            sockopts.append((socket.IPPROTO_TCP,
                             socket.TCP_KEEPINTVL, 30))  # pylint: disable=no-member
            sockopts.append((socket.IPPROTO_TCP,
                             socket.TCP_KEEPCNT, 8))  # pylint: disable=no-member

        self._con_pool_size = con_pool_size

        kwargs = dict(
            maxsize=con_pool_size,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            socket_options=sockopts,
            timeout=urllib3.Timeout(
                connect=self._connect_timeout, read=read_timeout, total=None))

        # Set a proxy according to the following order:
        # * proxy defined in proxy_url (+ urllib3_proxy_kwargs)
        # * proxy set in `HTTPS_PROXY` env. var.
        # * proxy set in `https_proxy` env. var.
        # * None (if no proxy is configured)

        if not proxy_url:
            proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        if not proxy_url:
            if appengine.is_appengine_sandbox():
                # Use URLFetch service if running in App Engine
                mgr = appengine.AppEngineManager()
            else:
                mgr = urllib3.PoolManager(**kwargs)
        else:
            kwargs.update(urllib3_proxy_kwargs)
            if proxy_url.startswith('socks'):
                try:
                    from telegram.vendor.ptb_urllib3.urllib3.contrib.socks import SOCKSProxyManager
                except ImportError:
                    raise RuntimeError('PySocks is missing')
                mgr = SOCKSProxyManager(proxy_url, **kwargs)
            else:
                mgr = urllib3.proxy_from_url(proxy_url, **kwargs)
                if mgr.proxy.auth:
                    # TODO: what about other auth types?
                    auth_hdrs = urllib3.make_headers(proxy_basic_auth=mgr.proxy.auth)
                    mgr.proxy_headers.update(auth_hdrs)

        self._con_pool = mgr

    @property
    def con_pool_size(self):
        """The size of the connection pool used."""
        return self._con_pool_size

    def stop(self):
        self._con_pool.clear()

    @staticmethod
    def _parse(json_data):
        """Try and parse the JSON returned from Telegram.

        Returns:
            dict: A JSON parsed as Python dict with results - on error this dict will be empty.

        """

        try:
            decoded_s = json_data.decode('utf-8')
            data = json.loads(decoded_s)
        except UnicodeDecodeError:
            logging.getLogger(__name__).debug(
                'Logging raw invalid UTF-8 response:\n%r', json_data)
            raise TelegramError('Server response could not be decoded using UTF-8')
        except ValueError:
            raise TelegramError('Invalid server response')

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

    def _request_wrapper(self, *args, **kwargs):
        """Wraps urllib3 request for handling known exceptions.

        Args:
            args: unnamed arguments, passed to urllib3 request.
            kwargs: keyword arguments, passed tp urllib3 request.

        Returns:
            str: A non-parsed JSON text.

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
        except urllib3.exceptions.TimeoutError:
            raise TimedOut()
        except urllib3.exceptions.HTTPError as error:
            # HTTPError must come last as its the base urllib3 exception class
            # TODO: do something smart here; for now just raise NetworkError
            raise NetworkError('urllib3 HTTPError {0}'.format(error))

        if 200 <= resp.status <= 299:
            # 200-299 range are HTTP success statuses
            return resp.data

        try:
            message = self._parse(resp.data)
        except ValueError:
            message = 'Unknown HTTPError'

        if resp.status in (401, 403):
            raise Unauthorized(message)
        elif resp.status == 400:
            raise BadRequest(message)
        elif resp.status == 404:
            raise InvalidToken()
        elif resp.status == 409:
            raise Conflict(message)
        elif resp.status == 413:
            raise NetworkError('File too large. Check telegram api limits '
                               'https://core.telegram.org/bots/api#senddocument')

        elif resp.status == 502:
            raise NetworkError('Bad Gateway')
        else:
            raise NetworkError('{0} ({1})'.format(message, resp.status))

    def get(self, url, timeout=None):
        """Request an URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            timeout (:obj:`int` | :obj:`float`): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
          A JSON object.

        """
        urlopen_kwargs = {}

        if timeout is not None:
            urlopen_kwargs['timeout'] = Timeout(read=timeout, connect=self._connect_timeout)

        result = self._request_wrapper('GET', url, **urlopen_kwargs)
        return self._parse(result)

    def post(self, url, data, timeout=None):
        """Request an URL.

        Args:
            url (:obj:`str`): The web location we want to retrieve.
            data (dict[str, str|int]): A dict of key/value pairs. Note: On py2.7 value is unicode.
            timeout (:obj:`int` | :obj:`float`): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

        Returns:
          A JSON object.

        """
        urlopen_kwargs = {}

        if timeout is not None:
            urlopen_kwargs['timeout'] = Timeout(read=timeout, connect=self._connect_timeout)

        # Are we uploading files?
        files = False

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
                    if isinstance(val.media, InputFile):
                        data[val.media.attach] = val.media.field_tuple
                else:
                    # Attach and set val to attached name for all
                    media = []
                    for m in val:
                        media.append(m.to_dict())
                        if isinstance(m.media, InputFile):
                            data[m.media.attach] = m.media.field_tuple
                    data[key] = json.dumps(media)
                files = True

        # Use multipart upload if we're uploading files, otherwise use JSON
        if files:
            result = self._request_wrapper('POST', url, fields=data, **urlopen_kwargs)
        else:
            result = self._request_wrapper('POST', url,
                                           body=json.dumps(data).encode('utf-8'),
                                           headers={'Content-Type': 'application/json'},
                                           **urlopen_kwargs)

        return self._parse(result)

    def retrieve(self, url, timeout=None):
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

    def download(self, url, filename, timeout=None):
        """Download a file by its URL.

        Args:
            url (str): The web location we want to retrieve.
            timeout (:obj:`int` | :obj:`float`): If this value is specified, use it as the read
                timeout from the server (instead of the one specified during creation of the
                connection pool).

          filename:
            The filename within the path to download the file.

        """
        buf = self.retrieve(url, timeout=timeout)
        with open(filename, 'wb') as fobj:
            fobj.write(buf)
