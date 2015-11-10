#!/usr/bin/env python
# pylint: disable=no-name-in-module,unused-import
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
from ssl import SSLError

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, urlretrieve, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode, urlretrieve
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
    data = json.loads(json_data.decode())

    if not data.get('ok') and data.get('description'):
        return data['description']

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
    if "timeout" in data:
        timeout = data["timeout"] + 1.
    else:
        timeout = None

    try:
        if InputFile.is_inputfile(data):
            data = InputFile(data)
            request = Request(url,
                              data=data.to_form(),
                              headers=data.headers)
        else:
            data = json.dumps(data)
            request = Request(url,
                              data=data.encode(),
                              headers={'Content-Type': 'application/json'})

        result = urlopen(request, timeout=timeout).read()
    except HTTPError as error:
        if error.getcode() == 403:
            raise TelegramError('Unauthorized')
        if error.getcode() == 502:
            raise TelegramError('Bad Gateway')

        message = _parse(error.read())
        raise TelegramError(message)
    except SSLError as error:
        if "The read operation timed out" == error.message:
            raise TelegramError("Timed out")

        raise TelegramError(error.message)
    return _parse(result)


def download(url,
             filename):
    """Download a file by its URL.
    Args:
      url:
        The web location we want to retrieve.

      filename:
        The filename wihtin the path to download the file.
    """

    urlretrieve(url, filename)
