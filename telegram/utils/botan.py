#!/usr/bin/env python

import json
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

H = NullHandler()
logging.getLogger(__name__).addHandler(H)


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
        data = json.dumps(message.__dict__)
        try:
            url = self.url_template.format(token=str(self.token),
                                           uid=str(uid),
                                           name=quote(event_name))
            request = Request(url,
                              data=data.encode(),
                              headers={'Content-Type': 'application/json'})
            response = urlopen(request)
            if response.getcode() != 200:
                return False
            return True
        except HTTPError as error:
            self.logger.warn('Botan track error ' +
                             str(error.code) + ':' + error.read().decode('utf-8'))
            return False
        except URLError as error:
            self.logger.warn('Botan track error ' + error.reason)
            return False
