#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
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
"""This module contains methods to make POST and GET requests"""

try:
    import ujson as json
except ImportError:
    import json
import os
import socket
import logging

import certifi
import urllib3
from urllib3.connection import HTTPConnection

from telegram import (InputFile, TelegramError)
from telegram.error import Unauthorized, NetworkError, TimedOut, BadRequest, ChatMigrated, \
    RetryAfter

logging.getLogger('urllib3').setLevel(logging.WARNING)


class Request(object):
    """
    Helper class for python-telegram-bot which provides methods to perform POST & GET towards
    telegram servers.

    Args:
        proxy_url (str): The URL to the proxy server. For example: `http://127.0.0.1:3128`.
        urllib3_proxy_kwargs (dict): Arbitrary arguments passed as-is to `urllib3.ProxyManager`.
            This value will be ignored if proxy_url is not set.

    """

    def __init__(self, con_pool_size=1, proxy_url=None, urllib3_proxy_kwargs=None):
        if urllib3_proxy_kwargs is None:
            urllib3_proxy_kwargs = dict()

        kwargs = dict(
            maxsize=con_pool_size,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            socket_options=HTTPConnection.default_socket_options + [
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            ])

        # Set a proxy according to the following order:
        # * proxy defined in proxy_url (+ urllib3_proxy_kwargs)
        # * proxy set in `HTTPS_PROXY` env. var.
        # * proxy set in `https_proxy` env. var.
        # * None (if no proxy is configured)

        if not proxy_url:
            proxy_url = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        if not proxy_url:
            mgr = urllib3.PoolManager(**kwargs)
        else:
            kwargs.update(urllib3_proxy_kwargs)
            mgr = urllib3.proxy_from_url(proxy_url, **kwargs)
            if mgr.proxy.auth:
                # TODO: what about other auth types?
                auth_hdrs = urllib3.make_headers(proxy_basic_auth=mgr.proxy.auth)
                mgr.proxy_headers.update(auth_hdrs)

        self._con_pool = mgr

    def stop(self):
        self._con_pool.clear()

    @staticmethod
    def _parse(json_data):
        """Try and parse the JSON returned from Telegram.

        Returns:
            dict: A JSON parsed as Python dict with results - on error this dict will be empty.

        """
        decoded_s = json_data.decode('utf-8')
        try:
            data = json.loads(decoded_s)
        except ValueError:
            raise TelegramError('Invalid server response')

        if not data.get('ok'):
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
            raise NetworkError('Unknown HTTPError {0}'.format(resp.status))

        if resp.status in (401, 403):
            raise Unauthorized()
        elif resp.status == 400:
            raise BadRequest(repr(message))
        elif resp.status == 502:
            raise NetworkError('Bad Gateway')
        else:
            raise NetworkError('{0} ({1})'.format(message, resp.status))

    def get(self, url):
        """Request an URL.
        Args:
          url:
            The web location we want to retrieve.

        Returns:
          A JSON object.

        """
        result = self._request_wrapper('GET', url)
        return self._parse(result)

    def post(self, url, data, timeout=None):
        """Request an URL.
        Args:
          url:
            The web location we want to retrieve.
          data:
            A dict of (str, unicode) key/value pairs.
          timeout:
            float. If this value is specified, use it as the definitive timeout (in
            seconds) for urlopen() operations. [Optional]

        Notes:
          If neither `timeout` nor `data['timeout']` is specified. The underlying
          defaults are used.

        Returns:
          A JSON object.

        """
        urlopen_kwargs = {}

        if timeout is not None:
            urlopen_kwargs['timeout'] = timeout

        if InputFile.is_inputfile(data):
            data = InputFile(data)
            result = self._request_wrapper('POST', url, body=data.to_form(), headers=data.headers)
        else:
            data = json.dumps(data)
            result = self._request_wrapper(
                'POST',
                url,
                body=data.encode(),
                headers={'Content-Type': 'application/json'},
                **urlopen_kwargs)

        return self._parse(result)

    def download(self, url, filename):
        """Download a file by its URL.
        Args:
          url:
            The web location we want to retrieve.

          filename:
            The filename within the path to download the file.

        """
        buf = self._request_wrapper('GET', url)
        with open(filename, 'wb') as fobj:
            fobj.write(buf)
