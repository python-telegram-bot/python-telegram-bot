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

import functools
import json
import socket
from ssl import SSLError

from future.moves.http.client import HTTPException
from future.moves.urllib.error import HTTPError, URLError
from future.moves.urllib.request import urlopen, urlretrieve, Request

from telegram import (InputFile, TelegramError)
from telegram.error import Unauthorized, NetworkError, TimedOut


def _parse(json_data):
    """Try and parse the JSON returned from Telegram and return an empty
    dictionary if there is any error.

    Args:
      url:
        urllib.urlopen object

    Returns:
      A JSON parsed as Python dict with results.
    """
    decoded_s = json_data.decode('utf-8')
    try:
        data = json.loads(decoded_s)
    except ValueError:
        raise TelegramError('Invalid server response')

    if not data.get('ok') and data.get('description'):
        return data['description']

    return data['result']


def _try_except_req(func):
    """Decorator for requests to handle known exceptions"""

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except HTTPError as error:
            # `HTTPError` inherits from `URLError` so `HTTPError` handling must
            # come first.
            errcode = error.getcode()

            if errcode in (401, 403):
                raise Unauthorized()
            elif errcode == 502:
                raise NetworkError('Bad Gateway')

            try:
                message = _parse(error.read())
            except ValueError:
                message = 'Unknown HTTPError {0}'.format(error.getcode())

            raise NetworkError('{0} ({1})'.format(message, errcode))

        except URLError as error:
            raise NetworkError('URLError: {0}'.format(error.reason))

        except (SSLError, socket.timeout) as error:
            err_s = str(error)
            if 'operation timed out' in err_s:
                raise TimedOut()

            raise NetworkError(err_s)

        except HTTPException as error:
            raise NetworkError('HTTPException: {0!r}'.format(error))

        except socket.error as error:
            raise NetworkError('socket.error: {0!r}'.format(error))

    return decorator


@_try_except_req
def get(url):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.

    Returns:
      A JSON object.
    """
    result = urlopen(url).read()

    return _parse(result)


@_try_except_req
def post(url, data, timeout=None):
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
        request = Request(url, data=data.to_form(), headers=data.headers)
    else:
        data = json.dumps(data)
        request = Request(url, data=data.encode(), headers={'Content-Type': 'application/json'})

    result = urlopen(request, **urlopen_kwargs).read()
    return _parse(result)


@_try_except_req
def download(url, filename):
    """Download a file by its URL.
    Args:
      url:
        The web location we want to retrieve.

      filename:
        The filename within the path to download the file.
    """

    urlretrieve(url, filename)
