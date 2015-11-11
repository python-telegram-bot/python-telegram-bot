#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
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

"""This module contains a object that represents a Telegram Bot"""

import functools
import logging

from telegram import (User, Message, Update, UserProfilePhotos, File,
                      TelegramError, ReplyMarkup, TelegramObject, NullHandler)
from telegram.utils import request

H = NullHandler()
logging.getLogger(__name__).addHandler(H)


class Bot(TelegramObject):

    """This object represents a Telegram Bot.

    Attributes:
        id (int):
        first_name (str):
        last_name (str):
        username (str):
        name (str):

    Args:
        token (str):
        **kwargs: Arbitrary keyword arguments.

    Keyword Args:
        base_url (Optional[str]):
    """

    def __init__(self,
                 token,
                 base_url=None):
        self.token = token

        if base_url is None:
            self.base_url = 'https://api.telegram.org/bot%s' % self.token
        else:
            self.base_url = base_url + self.token

        self.base_file_url = 'https://api.telegram.org/file/bot%s' % self.token

        self.bot = None

        self.logger = logging.getLogger(__name__)

    def info(func):
        """
        Returns:
        """
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            """
            decorator
            """
            if not self.bot:
                self.getMe()

            result = func(self, *args, **kwargs)
            return result
        return decorator

    @property
    @info
    def id(self):
        """int: """
        return self.bot.id

    @property
    @info
    def first_name(self):
        """str: """
        return self.bot.first_name

    @property
    @info
    def last_name(self):
        """str: """
        return self.bot.last_name

    @property
    @info
    def username(self):
        """str: """
        return self.bot.username

    @property
    def name(self):
        """str: """
        return '@%s' % self.username

    def log(func):
        """
        Returns:
          A telegram.Message instance representing the message posted.
        """
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            """
            decorator
            """
            logger.debug('Entering: %s', func.__name__)
            result = func(self, *args, **kwargs)
            logger.debug(result)
            logger.debug('Exiting: %s', func.__name__)
            return result
        return decorator

    def message(func):
        """
        Returns:
          A telegram.Message instance representing the message posted.
        """
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            """
            decorator
            """
            url, data = func(self, *args, **kwargs)

            if not data.get('chat_id'):
                raise TelegramError('Invalid chat_id')

            if kwargs.get('reply_to_message_id'):
                reply_to_message_id = kwargs.get('reply_to_message_id')
                data['reply_to_message_id'] = reply_to_message_id

            if kwargs.get('reply_markup'):
                reply_markup = kwargs.get('reply_markup')
                if isinstance(reply_markup, ReplyMarkup):
                    data['reply_markup'] = reply_markup.to_json()
                else:
                    data['reply_markup'] = reply_markup

            result = request.post(url, data)

            if result is True:
                return result

            return Message.de_json(result)
        return decorator

    @log
    def getMe(self):
        """A simple method for testing your bot's auth token.

        Returns:
          A telegram.User instance representing that bot if the
          credentials are valid, None otherwise.
        """
        url = '%s/getMe' % self.base_url

        result = request.get(url)

        self.bot = User.de_json(result)

        return self.bot

    @log
    @message
    def sendMessage(self,
                    chat_id,
                    text,
                    parse_mode=None,
                    disable_web_page_preview=None,
                    **kwargs):
        """Use this method to send text messages.

        Args:
          chat_id:
            Unique identifier for the message recipient - telegram.User or
            telegram.GroupChat id.
          parse_mode:
            Send Markdown, if you want Telegram apps to show bold, italic and
            inline URLs in your bot's message. For the moment, only Telegram
            for Android supports this. [Optional]
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

        if parse_mode:
            data['parse_mode'] = parse_mode
        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview

        return url, data

    @log
    @message
    def forwardMessage(self,
                       chat_id,
                       from_chat_id,
                       message_id):
        """Use this method to forward messages of any kind.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          from_chat_id:
            Unique identifier for the chat where the original message was sent
            - User or GroupChat id.
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
    def sendPhoto(self,
                  chat_id,
                  photo,
                  caption=None,
                  **kwargs):
        """Use this method to send photos.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
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
    def sendAudio(self,
                  chat_id,
                  audio,
                  duration=None,
                  performer=None,
                  title=None,
                  **kwargs):
        """Use this method to send audio files, if you want Telegram clients to
        display them in the music player. Your audio must be in an .mp3 format.
        On success, the sent Message is returned. Bots can currently send audio
        files of up to 50 MB in size, this limit may be changed in the future.

        For backward compatibility, when both fields title and description are
        empty and mime-type of the sent file is not "audio/mpeg", file is sent
        as playable voice message. In this case, your audio must be in an .ogg
        file encoded with OPUS. This will be removed in the future. You need to
        use sendVoice method instead.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          audio:
            Audio file to send. You can either pass a file_id as String to
            resend an audio that is already on the Telegram servers, or upload
            a new audio file using multipart/form-data.
          duration:
            Duration of sent audio in seconds. [Optional]
          performer:
            Performer of sent audio. [Optional]
          title:
            Title of sent audio. [Optional]
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

        if duration:
            data['duration'] = duration
        if performer:
            data['performer'] = performer
        if title:
            data['title'] = title

        return url, data

    @log
    @message
    def sendDocument(self,
                     chat_id,
                     document,
                     filename=None,
                     **kwargs):
        """Use this method to send general files.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          document:
            File to send. You can either pass a file_id as String to resend a
            file that is already on the Telegram servers, or upload a new file
            using multipart/form-data.
          filename:
            File name that shows in telegram message (it is usefull when you
            send file generated by temp module, for example). [Optional]
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

        if filename:
            data['filename'] = filename

        return url, data

    @log
    @message
    def sendSticker(self,
                    chat_id,
                    sticker,
                    **kwargs):
        """Use this method to send .webp stickers.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
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
    def sendVideo(self,
                  chat_id,
                  video,
                  duration=None,
                  caption=None,
                  **kwargs):
        """Use this method to send video files, Telegram clients support mp4
        videos (other formats may be sent as telegram.Document).

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          video:
            Video to send. You can either pass a file_id as String to resend a
            video that is already on the Telegram servers, or upload a new
            video file using multipart/form-data.
          duration:
            Duration of sent video in seconds. [Optional]
          caption:
            Video caption (may also be used when resending videos by file_id).
            [Optional]
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

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption

        return url, data

    @log
    @message
    def sendVoice(self,
                  chat_id,
                  voice,
                  duration=None,
                  **kwargs):
        """Use this method to send audio files, if you want Telegram clients to
        display the file as a playable voice message. For this to work, your
        audio must be in an .ogg file encoded with OPUS (other formats may be
        sent as Audio or Document). On success, the sent Message is returned.
        Bots can currently send audio files of up to 50 MB in size, this limit
        may be changed in the future.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          voice:
            Audio file to send. You can either pass a file_id as String to
            resend an audio that is already on the Telegram servers, or upload
            a new audio file using multipart/form-data.
          duration:
            Duration of sent audio in seconds. [Optional]
          reply_to_message_id:
            If the message is a reply, ID of the original message. [Optional]
          reply_markup:
            Additional interface options. A JSON-serialized object for a
            custom reply keyboard, instructions to hide keyboard or to force a
            reply from the user. [Optional]

        Returns:
          A telegram.Message instance representing the message posted.
        """

        url = '%s/sendVoice' % self.base_url

        data = {'chat_id': chat_id,
                'voice': voice}

        if duration:
            data['duration'] = duration

        return url, data

    @log
    @message
    def sendLocation(self,
                     chat_id,
                     latitude,
                     longitude,
                     **kwargs):
        """Use this method to send point on the map.

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
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
    def sendChatAction(self,
                       chat_id,
                       action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its
        typing status).

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          action:
            Type of action to broadcast. Choose one, depending on what the user
            is about to receive:
            - ChatAction.TYPING for text messages,
            - ChatAction.UPLOAD_PHOTO for photos,
            - ChatAction.UPLOAD_VIDEO for videos,
            - ChatAction.UPLOAD_AUDIO for audio files,
            - ChatAction.UPLOAD_DOCUMENT for general files,
            - ChatAction.FIND_LOCATION for location data.
        """

        url = '%s/sendChatAction' % self.base_url

        data = {'chat_id': chat_id,
                'action': action}

        return url, data

    @log
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
            Limits the number of photos to be retrieved. Values between 1-100
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

        result = request.post(url, data)

        return UserProfilePhotos.de_json(result)

    @log
    def getFile(self,
                file_id):
        """Use this method to get basic info about a file and prepare it for
        downloading. For the moment, bots can download files of up to 20MB in
        size.

        Args:
          file_id:
            File identifier to get info about.

        Returns:
          Returns a telegram.File object
        """

        url = '%s/getFile' % self.base_url

        data = {'file_id': file_id}

        result = request.post(url, data)

        if result.get('file_path'):
            result['file_path'] = '%s/%s' % (self.base_file_url,
                                             result['file_path'])

        return File.de_json(result)

    @log
    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0,
                   network_delay=2.):
        """Use this method to receive incoming updates using long polling.

        Args:
          offset:
            Identifier of the first update to be returned. Must be greater by
            one than the highest among the identifiers of previously received
            updates. By default, updates starting with the earliest unconfirmed
            update are returned. An update is considered confirmed as soon as
            getUpdates is called with an offset higher than its update_id.
          limit:
            Limits the number of updates to be retrieved. Values between 1-100
            are accepted. Defaults to 100.
          timeout:
            Timeout in seconds for long polling. Defaults to 0, i.e. usual
            short polling.
          network_delay:
            Additional timeout in seconds to allow the response from Telegram
            to take some time when using long polling. Defaults to 2, which
            should be enough for most connections. Increase it if it takes very
            long for data to be transmitted from and to the Telegram servers.

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

        result = request.post(url, data, network_delay=network_delay)

        if result:
            self.logger.info(
                'Getting updates: %s', [u['update_id'] for u in result])
        else:
            self.logger.info('No new updates found.')

        return [Update.de_json(x) for x in result]

    @log
    def setWebhook(self,
                   webhook_url=None,
                   certificate=None):
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

        data = {}
        if webhook_url:
            data['url'] = webhook_url
        if certificate:
            data['certificate'] = certificate

        result = request.post(url, data)

        return result

    @staticmethod
    def de_json(data):
        pass

    def to_dict(self):
        """
        Returns:
            dict:
        """
        data = {'id': self.id,
                'username': self.username,
                'first_name': self.username}
        if self.last_name:
            data['last_name'] = self.last_name
        return data

    def __reduce__(self):
        return (self.__class__, (self.token,
                                 self.base_url.replace(self.token, '')))
