#!/usr/bin/env python

import json

try:
    from urllib.request import urlopen, Request
    from urllib.parse import quote
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request
    from urllib import quote
    from urllib2 import URLError


class Botan(object):
    token = ''
    url_template = 'https://api.botan.io/track?' \
                   'token={token}&uid={uid}&name={name}'

    def __init__(self, token):
        self.token = token

    def track(self, message, event_name='event'):
        try:
            uid = message.chat_id
        except AttributeError:
            print('no chat_id in message')
            return False
        data = json.dumps(message.__dict__)
        try:
            url = self.url_template.format(token=str(self.token),
                                           uid=str(uid),
                                           name=quote(event_name))
            request = Request(url,
                              data=data,
                              headers={'Content-Type': 'application/json'})
            response = urlopen(request, json.dumps(data))
            if response.getcode() != 200:
                return False
            return True
        except URLError as error:
            print('botan track error ' + str(error.code) + ':' + error.reason)
            print(url)
            return False
