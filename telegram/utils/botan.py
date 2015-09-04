#!/usr/bin/env python
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

import json
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError, URLError

DEFAULT_BASE_URL = \
    'https://api.botan.io/track?token=%(token)&uid=%(uid)&name=%(name)'
USER_AGENT = 'Python Telegram Bot' \
             ' (https://github.com/leandrotoledo/python-telegram-bot)'
CONTENT_TYPE = 'application/json'

class Botan(Object):
    def __init__(self,
                 token,
                 base_url=None):
        self.token = token

        if base_url is None:
            self.base_url = DEFAULT_BASE_URL % {'token': self.token}
        else:
            self.base_url = base_url % {'token': self.token}

    def track(self,
              uid,
              text,
              name = 'Message'):

        url = self.base_url % {'uid': uid,
                               'message': text,
                               'name': name}

        self._post(url, message)

    def _post(self,
              url,
              data):
        headers = {'User-agent': USER_AGENT,
                   'Content-type': CONTENT_TYPE}

        try:
            request = Request(
                url,
                data=urlencode(data).encode(),
                headers=headers
            )

            return urlopen(request).read()
        except IOError as e:
            raise TelegramError(str(e))
        except HTTPError as e:
            raise TelegramError(str(e))
