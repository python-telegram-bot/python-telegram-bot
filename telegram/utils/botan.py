#!/usr/bin/env python

import logging
from telegram import NullHandler

try:
    from urllib.request import urlopen, Request
    from urllib.parse import quote
    from urllib.error import URLError, HTTPError
except ImportError:
    from urllib2 import urlopen, Request
    from urllib import quote
    from urllib2 import URLError, HTTPError

logging.getLogger(__name__).addHandler(NullHandler())


class Botan(object):
    """This class helps to send incoming events in your botan analytics account.
     See more: https://github.com/botanio/sdk#botan-sdk"""

    token = ''
    url_template = 'https://api.botan.io/track?token={token}' \
                   '&uid={uid}&name={name}&src=python-telegram-bot'

    def __init__(self, token):
        self.token = token
        self.logger = logging.getLogger(__name__)

    def track(self, message, event_name='event'):
        try:
            uid = message.chat_id
        except AttributeError:
            self.logger.warn('No chat_id in message')
            return False
        data = message.to_json()
        try:
            url = self.url_template.format(token=str(self.token),
                                           uid=str(uid),
                                           name=quote(event_name))
            request = Request(url,
                              data=data.encode(),
                              headers={'Content-Type': 'application/json'})
            urlopen(request)
            return True
        except HTTPError as error:
            self.logger.warn('Botan track error ' + str(error.code) + ':' + error.read().decode(
                'utf-8'))
            return False
        except URLError as error:
            self.logger.warn('Botan track error ' + str(error.reason))
            return False
