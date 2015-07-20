#!/usr/bin/env python
# encoding: utf-8

"""A library that provides a Python interface to the Telegram Bot API"""

import json
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request
    from urllib2 import HTTPError, URLError
import functools
import logging

from telegram import (User, Message, Update, UserProfilePhotos, TelegramError,
                      ReplyMarkup, InputFile, TelegramObject)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Bot(TelegramObject):

    def __init__(self,
                 token,
                 base_url=None,
                 debug=False):
        self.token = token

        if base_url is None:
            self.base_url = 'https://api.telegram.org/bot%s' % self.token
        else:
            self.base_url = base_url + self.token

        self.log = logging.getLogger(__name__)
        if debug:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

        try:
            bot = self.getMe()

            self.id = bot.id
            self.first_name = bot.first_name
            self.last_name = bot.last_name
            self.username = bot.username

            self.__auth = True

            self.log.info('Starting bot %s' % self.name)
        except TelegramError:
            raise TelegramError({'message': 'Bad token'})

    @property
    def name(self):
        return '@%s' % self.username

    def log(func):
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            logger.debug('Entering: %s' % func.__name__)
            result = func(self, *args, **kwargs)
            logger.debug(result)
            logger.debug('Exiting: %s' % func.__name__)
            return result
        return decorator

    def message(func):
        """
        Returns:
          A telegram.Message instance representing the message posted.
        """
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            url, data = func(self, *args, **kwargs)

            if kwargs.get('reply_to_message_id'):
                reply_to_message_id = kwargs.get('reply_to_message_id')
                data['reply_to_message_id'] = reply_to_message_id

            if kwargs.get('reply_markup'):
                reply_markup = kwargs.get('reply_markup')
                if isinstance(reply_markup, ReplyMarkup):
                    data['reply_markup'] = reply_markup.to_json()
                else:
                    data['reply_markup'] = reply_markup

            json_data = self._requestUrl(url, 'POST', data=data)
            data = self._parseAndCheckTelegram(json_data)

            if data is True:
                return data

            return Message.de_json(data)
        return decorator

    def require_authentication(func):
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            if not self.__auth:
                raise TelegramError({'message': "API must be authenticated."})

            return func(self, *args, **kwargs)
        return decorator

    @log
    @require_authentication
    def clearCredentials(self):
        """Clear any credentials for this instance.
        """
        self.__auth = False

    @log
    def getMe(self):
        """A simple method for testing your bot's auth token.

        Returns:
          A telegram.User instance representing that bot if the
          credentials are valid, None otherwise.
        """
        url = '%s/getMe' % self.base_url

        json_data = self._requestUrl(url, 'GET')
        data = self._parseAndCheckTelegram(json_data)

        return User.de_json(data)

    @log
    @message
    @require_authentication
    def sendMessage(self,
                    chat_id,
                    text,
                    disable_web_page_preview=None,
                    reply_to_message_id=None,
                    reply_markup=None):
        """Use this method to send text messages.

        Args:
          chat_id:
            Unique identifier for the message recipient — telegram.User or
            telegram.GroupChat id.
          text:
            Text of the message to be sent.
          disable_web_page_preview:
            Disables link previews for links in this message. [Optional]
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a custom
            reply keyboard, instructions to hide keyboard or to force a reply
            from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendMessage' % self.base_url

        data = {'chat_id': chat_id,
                'text': text}

        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview

        return url, data

    @log
    @message
    @require_authentication
    def forwardMessage(self,
                       chat_id,
                       from_chat_id,
                       message_id):
        """Use this method to forward messages of any kind.

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          from_chat_id:
            Unique identifier for the chat where the original message was sent
            — User or GroupChat id.
          message_id:
            Unique message identifier.

        Returns:
          A telegram.Message instance representing the message forwarded.
        """

        url = '%s/forwardMessage' % self.base_url

        data = {}
        if chat_id:
            data['chat_id'] = chat_id
        if from_chat_id:
            data['from_chat_id'] = from_chat_id
        if message_id:
            data['message_id'] = message_id

        return url, data

    @log
    @message
    @require_authentication
    def sendPhoto(self,
                  chat_id,
                  photo,
                  caption=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """Use this method to send photos.

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          photo:
            Photo to send. You can either pass a file_id as String to resend a
            photo that is already on the Telegram servers, or upload a new
            photo using multipart/form-data.
          caption:
            Photo caption (may also be used when resending photos by file_id).
            [Optional]
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a custom
            reply keyboard, instructions to hide keyboard or to force a reply
            from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendPhoto' % self.base_url

        data = {'chat_id': chat_id,
                'photo': photo}

        if caption:
            data['caption'] = caption

        return url, data

    @log
    @message
    @require_authentication
    def sendAudio(self,
                  chat_id,
                  audio,
                  reply_to_message_id=None,
                  reply_markup=None):
        """Use this method to send audio files, if you want Telegram clients to
        display the file as a playable voice message. For this to work, your
        audio must be in an .ogg file encoded with OPUS (other formats may be
        sent as telegram.Document).

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          audio:
            Audio file to send. You can either pass a file_id as String to
            resend an audio that is already on the Telegram servers, or upload
            a new audio file using multipart/form-data.
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendAudio' % self.base_url

        data = {'chat_id': chat_id,
                'audio': audio}

        return url, data

    @log
    @message
    @require_authentication
    def sendDocument(self,
                     chat_id,
                     document,
                     reply_to_message_id=None,
                     reply_markup=None):
        """Use this method to send general files.

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          document:
            File to send. You can either pass a file_id as String to resend a
            file that is already on the Telegram servers, or upload a new file
            using multipart/form-data.
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendDocument' % self.base_url

        data = {'chat_id': chat_id,
                'document': document}

        return url, data

    @log
    @message
    @require_authentication
    def sendSticker(self,
                    chat_id,
                    sticker,
                    reply_to_message_id=None,
                    reply_markup=None):
        """Use this method to send .webp stickers.

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          sticker:
            Sticker to send. You can either pass a file_id as String to resend
            a sticker that is already on the Telegram servers, or upload a new
            sticker using multipart/form-data.
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendSticker' % self.base_url

        data = {'chat_id': chat_id,
                'sticker': sticker}

        return url, data

    @log
    @message
    @require_authentication
    def sendVideo(self,
                  chat_id,
                  video,
                  reply_to_message_id=None,
                  reply_markup=None):
        """Use this method to send video files, Telegram clients support mp4
        videos (other formats may be sent as telegram.Document).

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          video:
            Video to send. You can either pass a file_id as String to resend a
            video that is already on the Telegram servers, or upload a new
            video file using multipart/form-data.
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendVideo' % self.base_url

        data = {'chat_id': chat_id,
                'video': video}

        return url, data

    @log
    @message
    @require_authentication
    def sendLocation(self,
                     chat_id,
                     latitude,
                     longitude,
                     reply_to_message_id=None,
                     reply_markup=None):
        """Use this method to send point on the map.

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          latitude:
            Latitude of location.
          longitude:
            Longitude of location.
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendLocation' % self.base_url

        data = {'chat_id': chat_id,
                'latitude': latitude,
                'longitude': longitude}

        return url, data

    @log
    @message
    @require_authentication
    def sendChatAction(self,
                       chat_id,
                       action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its
        typing status).

        Args:
          chat_id:
            Unique identifier for the message recipient — User or GroupChat id.
          action:
            Type of action to broadcast. Choose one, depending on what the user
            is about to receive:
            - ChatAction.TYPING for text messages,
            - ChatAction.UPLOAD_PHOTO for photos,
            - ChatAction.UPLOAD_VIDEO or upload_video for videos,
            - ChatAction.UPLOAD_AUDIO or upload_audio for audio files,
            - ChatAction.UPLOAD_DOCUMENT for general files,
            - ChatAction.FIND_LOCATION for location data.
        """

        url = '%s/sendChatAction' % self.base_url

        data = {'chat_id': chat_id,
                'action': action}

        return url, data

    @log
    @require_authentication
    def getUserProfilePhotos(self,
                             user_id,
                             offset=None,
                             limit=100):
        """Use this method to get a list of profile pictures for a user.

        Args:
          user_id:
            Unique identifier of the target user.
          offset:
            Sequential number of the first photo to be returned. By default,
            all photos are returned. [Optional]
          limit:
            Limits the number of photos to be retrieved. Values between 1—100
            are accepted. Defaults to 100. [Optional]

        Returns:
          Returns a telegram.UserProfilePhotos object.
        """

        url = '%s/getUserProfilePhotos' % self.base_url

        data = {'user_id': user_id}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data)

        return UserProfilePhotos.de_json(data)

    @log
    @require_authentication
    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0):
        """Use this method to receive incoming updates using long polling.

        Args:
          offset:
            Identifier of the first update to be returned. Must be greater by
            one than the highest among the identifiers of previously received
            updates. By default, updates starting with the earliest unconfirmed
            update are returned. An update is considered confirmed as soon as
            getUpdates is called with an offset higher than its update_id.
          limit:
            Limits the number of updates to be retrieved. Values between 1—100
            are accepted. Defaults to 100.
          timeout:
            Timeout in seconds for long polling. Defaults to 0, i.e. usual
            short polling.

        Returns:
          A list of telegram.Update objects are returned.
        """

        url = '%s/getUpdates' % self.base_url

        data = {}
        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        if timeout:
            data['timeout'] = timeout

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data)

        if data:
            self.log.info(
                'Getting updates: %s' % [u['update_id'] for u in data])
        else:
            self.log.info('No new updates found.')

        return [Update.de_json(x) for x in data]

    @log
    @require_authentication
    def setWebhook(self,
                   webhook_url):
        """Use this method to specify a url and receive incoming updates via an
        outgoing webhook. Whenever there is an update for the bot, we will send
        an HTTPS POST request to the specified url, containing a
        JSON-serialized Update. In case of an unsuccessful request, we will
        give up after a reasonable amount of attempts.

        Args:
          url:
            HTTPS url to send updates to.
            Use an empty string to remove webhook integration

        Returns:
          True if successful else TelegramError was raised
        """
        url = '%s/setWebhook' % self.base_url

        data = {'url': webhook_url}

        json_data = self._requestUrl(url, 'POST', data=data)
        data = self._parseAndCheckTelegram(json_data)

        return True

    def _requestUrl(self,
                    url,
                    method,
                    data=None):
        """Request an URL.

        Args:
          url:
            The web location we want to retrieve.
          method:
            Either POST or GET.
          data:
            A dict of (str, unicode) key/value pairs.

        Returns:
          A JSON object.
        """

        if method == 'POST':
            try:
                if InputFile.is_inputfile(data):
                    data = InputFile(data)

                    request = Request(
                        url,
                        data=data.to_form(),
                        headers=data.headers
                    )

                    return urlopen(request).read()
                else:
                    return urlopen(
                        url,
                        urlencode(data).encode()
                    ).read()
            except IOError as e:
                raise TelegramError(str(e))
            except HTTPError as e:
                raise TelegramError(str(e))
            except URLError as e:
                raise TelegramError(str(e))

        if method == 'GET':
            try:
                return urlopen(url).read()
            except URLError as e:
                raise TelegramError(str(e))

        return 0  # if not a POST or GET request

    def _parseAndCheckTelegram(self,
                               json_data):
        """Try and parse the JSON returned from Telegram and return an empty
        dictionary if there is any error.

        Args:
          json_data:
            JSON results from Telegram Bot API.

        Returns:
          A JSON parsed as Python dict with results.
        """

        try:
            data = json.loads(json_data.decode())
            if not data['ok']:
                raise TelegramError(data['description'])
        except ValueError:
            if '<title>403 Forbidden</title>' in json_data:
                raise TelegramError({'message': 'API must be authenticated'})
            raise TelegramError({'message': 'JSON decoding'})

        return data['result']

    def to_dict(self):
        data = {'id': self.id,
                'username': self.username,
                'first_name': self.username}
        if self.last_name:
            data['last_name'] = self.last_name
        return data
