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

REQUESTS = False
try:
    import requests
    REQUESTS = True
except ImportError:
    pass

try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError

if REQUESTS:
    _universal_post = requests.post
else:
    _universal_post = Request

from telegram import (InputFile, TelegramError)


def retry(maxretries):
    """@retry(x) decorates a function to run x times
    if it doesn't return correctly.

    Args:
      maxretries:
        Max number of retries until exception is raised further.

    Returns:
      The decorated function.
    """
    def retry_decorator(func):
        def retry_wrapper(*args, **kwargs):
            # logger.debug('Trying {} with arguments: {}, {}.'
            #     .format(func.__name__, args, kwargs))
            usedtries = 0
            while usedtries <= (maxretries - 1):
                try:
                    reply = func(*args, **kwargs)
                    if reply:
                        # logger.debug(
                        #     'Reply: {}'.format(reply.replace('\n','\\n')))
                        pass
                    else:
                        # logger.debug(
                        #     'Reply: none')
                        pass
                    return reply
                except:
                    if usedtries < (maxretries - 1):
                        # logger.debug('Exception in {}: {}'
                        #     .format(func.__name__, args, kwargs))
                        usedtries += 1
                    else:
                        raise
        retry_wrapper.fc = func.func_code
        return retry_wrapper
    return retry_decorator

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

@retry(3)
def get(url, timeout=None):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.
      timeout:
        (optional) timeout in seconds. Raises exception 
        if request exceeds it.

    Returns:
      A JSON object.
    """
    
    kwargs = {}
    if not timeout is None:
        kwargs['timeout'] = timeout
    
    if REQUESTS:
        result = requests.get(url, **kwargs).content
    else:
        result = urlopen(url, **kwargs).read()

    return _parse(result)


@retry(3)
def post(url,
         data,
         timeout=None):
    """Request an URL.
    Args:
      url:
        The web location we want to retrieve.
      data:
        A dict of (str, unicode) key/value pairs.
      timeout:
        (optional) timeout in seconds. Raises exception 
        if request exceeds it.

    Returns:
      A JSON object.
    """
    try:
        if InputFile.is_inputfile(data):
            data = InputFile(data)
            kwargs = {
                'data': data.to_form(),
                'headers': data.headers
            }
        else:
            data = json.dumps(data)
            kwargs = {
                'data': data.encode(),
                'headers': {'Content-Type': 'application/json'}
            }
        if not timeout is None:
            kwargs['timeout'] = timeout
        request = _universal_post(url, **kwargs)
        if REQUESTS:
            request.raise_for_status()
            result = request.content
        else:
            result = urlopen(request).read()
    except HTTPError as error:
        if error.getcode() == 403:
            raise TelegramError('Unauthorized')

        message = _parse(error.read())
        raise TelegramError(message)

    return _parse(result)
