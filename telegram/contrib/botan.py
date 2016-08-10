import logging
from telegram import NullHandler

from future.moves.urllib.parse import quote
from future.moves.urllib.error import HTTPError, URLError
from future.moves.urllib.request import urlopen, Request

logging.getLogger(__name__).addHandler(NullHandler())


class Botan(object):
    """This class helps to send incoming events to your botan analytics account.
     See more: https://github.com/botanio/sdk#botan-sdk
    """

    token = ''
    url_template = 'https://api.botan.io/track?token={token}' \
                   '&uid={uid}&name={name}&src=python-telegram-bot'
    shorten_template = 'https://api.botan.io/s?token={token}' \
                       '&user_ids={user_ids}&url={url}&src=python-telegram-bot'

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

    def shorten(self, url, user_id):
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://' + url
        try:
            url2 = self.shorten_template.format(token=str(self.token),
                                                user_ids=str(user_id),
                                                url=str(url))
            request = Request(url2,
                              headers={'Content-Type': 'application/json'})
            with urlopen(request) as response:
                shortened_url = response.read()
            return shortened_url.decode('utf-8')
        except HTTPError as error:
            self.logger.warn('Botan track error ' + str(error.code) + ':' + error.read().decode(
                'utf-8'))
            return None
        except URLError as error:
            self.logger.warn('Botan track error ' + str(error.reason))
            return None
