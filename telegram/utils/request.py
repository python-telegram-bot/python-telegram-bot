#!/usr/bin/env python
# pylint: disable=no-name-in-module
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <leandrotoeldodesouza@gmail.com>
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

import json

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError, URLError

from telegram import (InputFile, TelegramError)


def _parse(json_data):
    """Try and parse the JSON returned from Telegram and return an empty
    dictionary if there is any error.

    Args:
      url:
        urllib.urlopen object

    Returns:
      A JSON parsed as Python dict with results.
    """
    try:
        data = json.loads(json_data.decode())

        if not data.get('ok') and data.get('description'):
            return data['description']
    except ValueError:
        raise TelegramError({'message': 'JSON decoding'})

    return data['result']


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


def post(url,
         data):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.
      data:
        A dict of (str, unicode) key/value pairs.

    Returns:
      A JSON object.
    """
    try:
        if InputFile.is_inputfile(data):
            data = InputFile(data)
            request = Request(url, data=data.to_form(), headers=data.headers)

            result = urlopen(request).read()
        else:
            result = urlopen(url, urlencode(data).encode()).read()
    except HTTPError as error:
        message = _parse(error.read())
        raise TelegramError(message)
    except URLError as error:
        raise TelegramError(str(error))
    except IOError as error:
        raise TelegramError(str(error))

    return _parse(result)
