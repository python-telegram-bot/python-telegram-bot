#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2016
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
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
"""This module contains an object that represents a Telegram Bot."""

import functools
import logging
import warnings

from telegram import (User, Message, Update, Chat, ChatMember, UserProfilePhotos, File,
                      ReplyMarkup, TelegramObject, WebhookInfo, GameHighScore)
from telegram.error import InvalidToken, TelegramError
from telegram.utils.request import Request

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Bot(TelegramObject):
    """This object represents a Telegram Bot.

    Attributes:
        id (int): Unique identifier for this bot.
        first_name (str): Bot's first name.
        last_name (str): Bot's last name.
        username (str): Bot's username.
        name (str): Bot's @username.

    Args:
        token (str): Bot's unique authentication.
        base_url (Optional[str]): Telegram Bot API service URL.
        base_file_url (Optional[str]): Telegram Bot API file URL.
        request (Optional[Request]): Pre initialized `Request` class.

    """

    def __init__(self, token, base_url=None, base_file_url=None, request=None):
        self.token = self._validate_token(token)

        if base_url is None:
            base_url = 'https://api.telegram.org/bot'

        if base_file_url is None:
            base_file_url = 'https://api.telegram.org/file/bot'

        self.base_url = str(base_url) + str(self.token)
        self.base_file_url = str(base_file_url) + str(self.token)
        self.bot = None
        self._request = request or Request()
        self.logger = logging.getLogger(__name__)

    @property
    def request(self):
        return self._request

    @staticmethod
    def _validate_token(token):
        """a very basic validation on token"""
        if any(x.isspace() for x in token):
            raise InvalidToken()

        left, sep, _right = token.partition(':')
        if (not sep) or (not left.isdigit()) or (len(left) < 3):
            raise InvalidToken()

        return token

    def info(func):

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            if not self.bot:
                self.getMe()

            result = func(self, *args, **kwargs)
            return result

        return decorator

    @property
    @info
    def id(self):
        return self.bot.id

    @property
    @info
    def first_name(self):
        return self.bot.first_name

    @property
    @info
    def last_name(self):
        return self.bot.last_name

    @property
    @info
    def username(self):
        return self.bot.username

    @property
    def name(self):
        return '@{0}'.format(self.username)

    def log(func):
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            logger.debug('Entering: %s', func.__name__)
            result = func(self, *args, **kwargs)
            logger.debug(result)
            logger.debug('Exiting: %s', func.__name__)
            return result

        return decorator

    def message(func):

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            url, data = func(self, *args, **kwargs)

            if kwargs.get('reply_to_message_id'):
                data['reply_to_message_id'] = kwargs.get('reply_to_message_id')

            if kwargs.get('disable_notification'):
                data['disable_notification'] = kwargs.get('disable_notification')

            if kwargs.get('reply_markup'):
                reply_markup = kwargs.get('reply_markup')
                if isinstance(reply_markup, ReplyMarkup):
                    data['reply_markup'] = reply_markup.to_json()
                else:
                    data['reply_markup'] = reply_markup

            result = self._request.post(url, data, timeout=kwargs.get('timeout'))

            if result is True:
                return result

            return Message.de_json(result, self)

        return decorator

    @log
    def getMe(self, timeout=None, **kwargs):
        """A simple method for testing your bot's auth token.

        Args:
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance representing that bot if the
                credentials are valid, `None` otherwise.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getMe'.format(self.base_url)

        result = self._request.get(url, timeout=timeout)

        self.bot = User.de_json(result, self)

        return self.bot

    @log
    @message
    def sendMessage(self,
                    chat_id,
                    text,
                    parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        """Use this method to send text messages.

        Args:
            chat_id (str): Unique identifier for the target chat or
                username of the target channel (in the format
                @channelusername).
            text (str): Text of the message to be sent. The current maximum
                length is 4096 UTF-8 characters.
            parse_mode (Optional[str]): Send Markdown or HTML, if you want
                Telegram apps to show bold, italic, fixed-width text or inline
                URLs in your bot's message.
            disable_web_page_preview (Optional[bool]): Disables link previews
                for links in this message.
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to remove reply
                keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendMessage'.format(self.base_url)

        data = {'chat_id': chat_id, 'text': text}

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
                       message_id,
                       disable_notification=False,
                       timeout=None,
                       **kwargs):
        """Use this method to forward messages of any kind.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            from_chat_id: Unique identifier for the chat where the original message was sent
                - Chat id.
            message_id: Unique message identifier.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message forwarded.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/forwardMessage'.format(self.base_url)

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
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        """Use this method to send photos.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            photo: Photo to send. You can either pass a file_id as String to resend a photo that is
                already on the Telegram servers, or upload a new photo using multipart/form-data.
            caption (Optional[str]): Photo caption (may also be used when resending photos by
                file_id).
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendPhoto'.format(self.base_url)

        data = {'chat_id': chat_id, 'photo': photo}

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
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
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
            chat_id: Unique identifier for the message recipient - Chat id.
            audio: Audio file to send. You can either pass a file_id as String to resend an audio
                that is already on the Telegram servers, or upload a new audio file using
                multipart/form-data.
            duration (Optional[int]): Duration of sent audio in seconds.
            performer (Optional[str]): Performer of sent audio.
            title (Optional[str]): Title of sent audio.
            caption (Optional[str]): Audio caption
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendAudio'.format(self.base_url)

        data = {'chat_id': chat_id, 'audio': audio}

        if duration:
            data['duration'] = duration
        if performer:
            data['performer'] = performer
        if title:
            data['title'] = title
        if caption:
            data['caption'] = caption

        return url, data

    @log
    @message
    def sendDocument(self,
                     chat_id,
                     document,
                     filename=None,
                     caption=None,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=None,
                     **kwargs):
        """Use this method to send general files.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            document: File to send. You can either pass a file_id as String to resend a file that
                is already on the Telegram servers, or upload a new file using multipart/form-data.
            filename (Optional[str]): File name that shows in telegram message (it is useful when
                you send file generated by temp module, for example).
            caption (Optional[str]): Document caption (may also be used when resending documents by
                file_id), 0-200 characters.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendDocument'.format(self.base_url)

        data = {'chat_id': chat_id, 'document': document}

        if filename:
            data['filename'] = filename
        if caption:
            data['caption'] = caption

        return url, data

    @log
    @message
    def sendSticker(self,
                    chat_id,
                    sticker,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        """Use this method to send .webp stickers.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            sticker: Sticker to send. You can either pass a file_id as String to resend a sticker
                that is already on the Telegram servers, or upload a new sticker using
                multipart/form-data.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendSticker'.format(self.base_url)

        data = {'chat_id': chat_id, 'sticker': sticker}

        return url, data

    @log
    @message
    def sendVideo(self,
                  chat_id,
                  video,
                  duration=None,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        """Use this method to send video files, Telegram clients support mp4
        videos (other formats may be sent as telegram.Document).

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            video: Video to send. You can either pass a file_id as String to resend a video that is
                already on the Telegram servers, or upload a new video file using
                multipart/form-data.
            duration (Optional[int]): Duration of sent video in seconds.
            caption (Optional[str]): Video caption (may also be used when resending videos by
                file_id).
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVideo'.format(self.base_url)

        data = {'chat_id': chat_id, 'video': video}

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
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        """Use this method to send audio files, if you want Telegram clients to display the file as
        a playable voice message. For this to work, your audio must be in an .ogg file encoded with
        OPUS (other formats may be sent as Audio or Document). On success, the sent Message is
        returned. Bots can currently send audio files of up to 50 MB in size, this limit may be
        changed in the future.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            voice: Audio file to send. You can either pass a file_id as String to resend an audio
                that is already on the Telegram servers, or upload a new audio file using
                multipart/form-data.
            duration (Optional[int]): Duration of sent audio in seconds.
            caption (Optional[str]): Voice caption
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVoice'.format(self.base_url)

        data = {'chat_id': chat_id, 'voice': voice}

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption

        return url, data

    @log
    @message
    def sendLocation(self,
                     chat_id,
                     latitude,
                     longitude,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=None,
                     **kwargs):
        """Use this method to send point on the map.

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            latitude (float): Latitude of location.
            longitude (float): Longitude of location.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendLocation'.format(self.base_url)

        data = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude}

        return url, data

    @log
    @message
    def sendVenue(self,
                  chat_id,
                  latitude,
                  longitude,
                  title,
                  address,
                  foursquare_id=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        """
        Use this method to send information about a venue.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            latitude (float): Latitude of the venue.
            longitude (float): Longitude of the venue.
            title (str): Name of the venue.
            address (str): Address of the venue.
            foursquare_id (Optional[str]): Foursquare identifier of the venue.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVenue'.format(self.base_url)

        data = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'title': title
        }

        if foursquare_id:
            data['foursquare_id'] = foursquare_id

        return url, data

    @log
    @message
    def sendContact(self,
                    chat_id,
                    phone_number,
                    first_name,
                    last_name=None,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        """
        Use this method to send phone contacts.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            phone_number (str): Contact's phone number.
            first_name (str): Contact's first name.
            last_name (Optional[str]): Contact's last name.
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply, ID of the original
                message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, instance representing the message posted.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendContact'.format(self.base_url)

        data = {'chat_id': chat_id, 'phone_number': phone_number, 'first_name': first_name}

        if last_name:
            data['last_name'] = last_name

        return url, data

    @log
    @message
    def sendGame(self,
                 chat_id,
                 game_short_name,
                 disable_notification=False,
                 reply_to_message_id=None,
                 reply_markup=None,
                 timeout=None,
                 **kwargs):
        """Use this method to send a game.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            game_short_name (str): Short name of the game, serves as the unique identifier for the
                game.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently. iOS users will not
                receive a notification, Android users will receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options.
                A JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            :class:`telegram.Message`: On success, the sent message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendGame'.format(self.base_url)

        data = {'chat_id': chat_id, 'game_short_name': game_short_name}

        return url, data

    @log
    @message
    def sendChatAction(self, chat_id, action, timeout=None, **kwargs):
        """Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status).

        Args:
            chat_id: Unique identifier for the message recipient - Chat id.
            action: Type of action to broadcast. Choose one, depending on what the user is about to
                receive:

                    - ChatAction.TYPING for text messages,
                    - ChatAction.UPLOAD_PHOTO for photos,
                    - ChatAction.UPLOAD_VIDEO for videos,
                    - ChatAction.UPLOAD_AUDIO for audio files,
                    - ChatAction.UPLOAD_DOCUMENT for general files,
                    - ChatAction.FIND_LOCATION for location data.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        """
        url = '{0}/sendChatAction'.format(self.base_url)

        data = {'chat_id': chat_id, 'action': action}

        return url, data

    @log
    def answerInlineQuery(self,
                          inline_query_id,
                          results,
                          cache_time=300,
                          is_personal=None,
                          next_offset=None,
                          switch_pm_text=None,
                          switch_pm_parameter=None,
                          timeout=None,
                          **kwargs):
        """Use this method to send answers to an inline query. No more than 50 results per query
        are allowed.

        Args:
            inline_query_id (str): Unique identifier for the answered query.
            results (list[:class:`telegram.InlineQueryResult`]): A list of results for the inline
                query.
            cache_time (Optional[int]): The maximum amount of time the result of the inline query
                may be cached on the server.
            is_personal (Optional[bool]): Pass `True`, if results may be cached on the server side
                only for the user that sent the query. By default, results may be returned to any
                user who sends the same query.
            next_offset (Optional[str]): Pass the offset that a client should send in the next
                query with the same text to receive more results. Pass an empty string if there are
                no more results or if you don't support pagination. Offset length can't exceed 64
                bytes.
            switch_pm_text (Optional[str]): If passed, clients will display a button with specified
                text that switches the user to a private chat with the bot and sends the bot a
                start message with the parameter switch_pm_parameter.
            switch_pm_parameter (Optional[str]): Parameter for the start message sent to the bot
                when user presses the switch button.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/answerInlineQuery'.format(self.base_url)

        results = [res.to_dict() for res in results]

        data = {'inline_query_id': inline_query_id, 'results': results}

        if cache_time or cache_time == 0:
            data['cache_time'] = cache_time
        if is_personal:
            data['is_personal'] = is_personal
        if next_offset is not None:
            data['next_offset'] = next_offset
        if switch_pm_text:
            data['switch_pm_text'] = switch_pm_text
        if switch_pm_parameter:
            data['switch_pm_parameter'] = switch_pm_parameter

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def getUserProfilePhotos(self, user_id, offset=None, limit=100, timeout=None, **kwargs):
        """Use this method to get a list of profile pictures for a user.

        Args:
            user_id: Unique identifier of the target user.
            offset (Optional[int]): Sequential number of the first photo to be returned. By
                default, all photos are returned.
            limit (Optional[int]): Limits the number of photos to be retrieved. Values between
                1-100 are accepted. Defaults to 100.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            list[:class:`telegram.UserProfilePhotos`]: A list of user profile photos objects is
                returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getUserProfilePhotos'.format(self.base_url)

        data = {'user_id': user_id}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        result = self._request.post(url, data, timeout=timeout)

        return UserProfilePhotos.de_json(result, self)

    @log
    def getFile(self, file_id, timeout=None, **kwargs):
        """Use this method to get basic info about a file and prepare it for downloading. For the
        moment, bots can download files of up to 20MB in size.

        Args:
            file_id: File identifier to get info about.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.File`: On success, a :class:`telegram.File` object is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getFile'.format(self.base_url)

        data = {'file_id': file_id}

        result = self._request.post(url, data, timeout=timeout)

        if result.get('file_path'):
            result['file_path'] = '%s/%s' % (self.base_file_url, result['file_path'])

        return File.de_json(result, self)

    @log
    def kickChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        """Use this method to kick a user from a group or a supergroup.

        In the case of supergroups, the user will not be able to return to the group on their own
        using invite links, etc., unless unbanned first. The bot must be an administrator in the
        group for this to work.

        Args:
            chat_id: Unique identifier for the target group or username of the target supergroup
                (in the format @supergroupusername).
            user_id: Unique identifier of the target user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/kickChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def unbanChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        """Use this method to unban a previously kicked user in a supergroup.
        The user will not return to the group automatically, but will be able to join via link,
        etc. The bot must be an administrator in the group for this to work.

        Args:
            chat_id: Unique identifier for the target group or username of the target supergroup
                (in the format @supergroupusername).
            user_id: Unique identifier of the target user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/unbanChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def answerCallbackQuery(self,
                            callback_query_id,
                            text=None,
                            show_alert=False,
                            url=None,
                            cache_time=None,
                            timeout=None,
                            **kwargs):
        """Use this method to send answers to callback queries sent from inline keyboards. The
        answer will be displayed to the user as a notification at the top of the chat screen or as
        an alert.

        Args:
            callback_query_id (str): Unique identifier for the query to be answered.
            text (Optional[str]): Text of the notification. If not specified, nothing will be shown
                to the user.
            show_alert (Optional[bool]): If `True`, an alert will be shown by the client instead of
                a notification at the top of the chat screen. Defaults to `False`.
            url (Optional[str]): URL that will be opened by the user's client.
            cache_time (Optional[int]): The maximum amount of time in seconds that the result of
                the callback query may be cached client-side. Telegram apps will support caching
                starting in version 3.14. Defaults to 0.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url_ = '{0}/answerCallbackQuery'.format(self.base_url)

        data = {'callback_query_id': callback_query_id}

        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert
        if url:
            data['url'] = url
        if cache_time is not None:
            data['cache_time'] = cache_time

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    @message
    def editMessageText(self,
                        text,
                        chat_id=None,
                        message_id=None,
                        inline_message_id=None,
                        parse_mode=None,
                        disable_web_page_preview=None,
                        reply_markup=None,
                        timeout=None,
                        **kwargs):
        """Use this method to edit text messages sent by the bot or via the bot (for inline bots).

        Args:
            text: New text of the message.
            chat_id: Required if inline_message_id is not specified. Unique identifier for the
                target chat or username of the target channel (in the format @channelusername).
            message_id: Required if inline_message_id is not specified. Unique identifier of the
                sent message.
            inline_message_id: Required if chat_id and message_id are not specified. Identifier of
                the inline message.
            parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic,
                fixed-width text or inline URLs in your bot's message.
            disable_web_page_preview: Disables link previews for links in this message.
            reply_markup: A JSON-serialized object for an inline keyboard.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the edited
                message is returned, otherwise `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/editMessageText'.format(self.base_url)

        data = {'text': text}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if parse_mode:
            data['parse_mode'] = parse_mode
        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview

        return url, data

    @log
    @message
    def editMessageCaption(self,
                           chat_id=None,
                           message_id=None,
                           inline_message_id=None,
                           caption=None,
                           reply_markup=None,
                           timeout=None,
                           **kwargs):
        """Use this method to edit captions of messages sent by the bot or via the bot (for inline
            bots).

        Args:
            chat_id (Optional[str]): Required if inline_message_id is not specified. Unique
                identifier for the target chat or username of the target channel (in the format
                @channelusername).
            message_id (Optional[str]): Required if inline_message_id is not specified. Unique
                identifier of the sent message.
            inline_message_id (Optional[str]): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            caption (Optional[str]): New caption of the message.
            reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): A JSON-serialized
                object for an inline keyboard.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the edited
                message is returned, otherwise `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise TelegramError(
                'editMessageCaption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        url = '{0}/editMessageCaption'.format(self.base_url)

        data = {}

        if caption:
            data['caption'] = caption
        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    @message
    def editMessageReplyMarkup(self,
                               chat_id=None,
                               message_id=None,
                               inline_message_id=None,
                               reply_markup=None,
                               timeout=None,
                               **kwargs):
        """Use this method to edit only the reply markup of messages sent by the bot or via the bot
        (for inline bots).

        Args:
            chat_id (Optional[str]): Required if inline_message_id is not specified. Unique
                identifier for the target chat or username of the target channel (in the format
                @channelusername).
            message_id (Optional[str]): Required if inline_message_id is not specified. Unique
                identifier of the sent message.
            inline_message_id (Optional[str]): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]): A JSON-serialized
                object for an inline keyboard.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by
            the bot, the edited message is returned, otherwise `True` is
            returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise TelegramError(
                'editMessageCaption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        url = '{0}/editMessageReplyMarkup'.format(self.base_url)

        data = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0,
                   network_delay=None,
                   read_latency=2.,
                   allowed_updates=None,
                   **kwargs):
        """Use this method to receive incoming updates using long polling.

        Args:
            offset (Optional[int]): Identifier of the first update to be returned. Must be greater
                by one than the highest among the identifiers of previously received updates. By
                default, updates starting with the earliest unconfirmed update are returned. An
                update is considered confirmed as soon as getUpdates is called with an offset
                higher than its update_id.
            limit (Optional[int]): Limits the number of updates to be retrieved. Values between
                1-100 are accepted. Defaults to 100.
            allowed_updates (Optional[list[str]]): List the types of updates you want your bot to
                receive. For example, specify
                ``["message", "edited_channel_post", "callback_query"]`` to only receive updates of
                these types. See ``telegram.Update`` for a complete list of available update types.
                Specify an empty list to receive all updates regardless of type (default). If not
                specified, the previous setting will be used.
                Please note that this parameter doesn't affect updates created before the call to
                the setWebhook, so unwanted updates may be received for a short period of time.
            timeout (Optional[int]): Timeout in seconds for long polling. Defaults to 0, i.e. usual
                short polling. Be careful not to set this timeout too high, as the connection might
                be dropped and there's no way of knowing it immediately (so most likely the failure
                will be detected after the timeout had passed).
            network_delay: Deprecated. Will be honoured as `read_latency` for a while but will be
                removed in the future.
            read_latency (Optional[float|int]): Grace time in seconds for receiving the reply from
                server. Will be added to the `timeout` value and used as the read timeout from
                server (Default: 2).
            **kwargs (dict): Arbitrary keyword arguments.

        Notes:
            The main problem with long polling is that a connection will be dropped and we won't
            be getting the notification in time for it. For that, we need to use long polling, but
            not too long as well read latency which is short, but not too short.
            Long polling improves performance, but if it's too long and the connection is dropped
            on many cases we won't know the connection dropped before the long polling timeout and
            the read latency time had passed. If you experience connection timeouts, you should
            tune these settings.

        Returns:
            list[:class:`telegram.Update`]

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getUpdates'.format(self.base_url)

        if network_delay is not None:
            warnings.warn('network_delay is deprecated, use read_latency instead')
            read_latency = network_delay

        data = {'timeout': timeout}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates

        # Ideally we'd use an aggressive read timeout for the polling. However,
        # * Short polling should return within 2 seconds.
        # * Long polling poses a different problem: the connection might have been dropped while
        #   waiting for the server to return and there's no way of knowing the connection had been
        #   dropped in real time.
        result = self._request.post(url, data, timeout=float(read_latency) + float(timeout))

        if result:
            self.logger.debug('Getting updates: %s', [u['update_id'] for u in result])
        else:
            self.logger.debug('No new updates found.')

        return [Update.de_json(u, self) for u in result]

    @log
    def setWebhook(self,
                   url=None,
                   certificate=None,
                   timeout=None,
                   max_connections=40,
                   allowed_updates=None,
                   **kwargs):
        """Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, we will send an HTTPS POST request to the
        specified url, containing a JSON-serialized Update. In case of an unsuccessful request, we
        will give up after a reasonable amount of attempts.

        Args:
            url: HTTPS url to send updates to. Use an empty string to remove webhook integration.
            certificate (file): Upload your public key certificate so that the root certificate in
                use can be checked.
            max_connections (Optional[int]): Maximum allowed number of simultaneous HTTPS
                connections to the webhook for update delivery, 1-100. Defaults to 40. Use lower
                values to limit the load on your bot's server, and higher values to increase your
                bot's throughput.
            allowed_updates (Optional[list[str]]): List the types of updates you want your bot to
                receive. For example, specify
                ``["message", "edited_channel_post", "callback_query"]`` to only receive updates of
                these types. See ``telegram.Update`` for a complete list of available update types.
                Specify an empty list to receive all updates regardless of type (default). If not
                specified, the previous setting will be used.
                Please note that this parameter doesn't affect updates created before the call to
                the setWebhook, so unwanted updates may be received for a short period of time.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url_ = '{0}/setWebhook'.format(self.base_url)

        # Backwards-compatibility: 'url' used to be named 'webhook_url'
        if 'webhook_url' in kwargs:
            warnings.warn("The 'webhook_url' parameter has been renamed to 'url' in accordance "
                          "with the API")

            if url is not None:
                raise ValueError("The parameters 'url' and 'webhook_url' are mutually exclusive")

            url = kwargs['webhook_url']
            del kwargs['webhook_url']

        data = {}

        if url is not None:
            data['url'] = url
        if certificate:
            data['certificate'] = certificate
        if max_connections is not None:
            data['max_connections'] = max_connections
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    def deleteWebhook(self, timeout=None, **kwargs):
        """Use this method to remove webhook integration if you decide to switch back to
        getUpdates. Returns True on success. Requires no parameters.

        Args:
            timeout (Optional[float]): If this value is specified, use it as the definitive timeout
                (in seconds) for urlopen() operations.
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/deleteWebhook'.format(self.base_url)

        data = {}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def leaveChat(self, chat_id, timeout=None, **kwargs):
        """Use this method for your bot to leave a group, supergroup or channel.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/leaveChat'.format(self.base_url)

        data = {'chat_id': chat_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def getChat(self, chat_id, timeout=None, **kwargs):
        """Use this method to get up to date information about the chat (current name of the user
        for one-on-one conversations, current username of a user, group or channel, etc.).

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Chat`: On success, :class:`telegram.Chat` is
            returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChat'.format(self.base_url)

        data = {'chat_id': chat_id}

        result = self._request.post(url, data, timeout=timeout)

        return Chat.de_json(result, self)

    @log
    def getChatAdministrators(self, chat_id, timeout=None, **kwargs):
        """Use this method to get a list of administrators in a chat. On success, returns an Array
        of ChatMember objects that contains information about all chat administrators except other
        bots. If the chat is a group or a supergroup and no administrators were appointed, only the
        creator will be returned.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            list[:class:`telegram.ChatMember`]: A list of chat member objects.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatAdministrators'.format(self.base_url)

        data = {'chat_id': chat_id}

        result = self._request.post(url, data, timeout=timeout)

        return [ChatMember.de_json(x, self) for x in result]

    @log
    def getChatMembersCount(self, chat_id, timeout=None, **kwargs):
        """Use this method to get the number of members in a chat.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            int: On success, an `int` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatMembersCount'.format(self.base_url)

        data = {'chat_id': chat_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def getChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        """Use this method to get information about a member of a chat.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in
                the format @channelusername).
            user_id: Unique identifier of the target user.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.ChatMember`: On success, chat member object is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        result = self._request.post(url, data, timeout=timeout)

        return ChatMember.de_json(result, self)

    def getWebhookInfo(self, timeout=None, **kwargs):
        """Use this method to get current webhook status.

        If the bot is using getUpdates, will return an object with the url field empty.

        Args:
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            :class: `telegram.WebhookInfo`

        """
        url = '{0}/getWebhookInfo'.format(self.base_url)

        data = {}

        result = self._request.post(url, data, timeout=timeout)

        return WebhookInfo.de_json(result, self)

    def setGameScore(self,
                     user_id,
                     score,
                     chat_id=None,
                     message_id=None,
                     inline_message_id=None,
                     edit_message=None,
                     force=None,
                     disable_edit_message=None,
                     timeout=None,
                     **kwargs):
        """Use this method to set the score of the specified user in a game.

        Args:
            user_id (int): User identifier.
            score (int): New score, must be non-negative.
            chat_id (Optional[int|str]): Required if `inline_message_id` is not specified. Unique
                identifier for the target chat (or username of the target channel in the format
                `@channelusername`)
            message_id (Optional[int]): Required if inline_message_id is not specified. Identifier
                of the sent message.
            inline_message_id (Optional[str]): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            force (Optional[bool]): Pass True, if the high score is allowed to decrease. This can
                be useful when fixing mistakes or banning cheaters.
            disable_edit_message (Optional[bool]): Pass True, if the game message should not be
                automatically edited to include the current scoreboard.
            edit_message (Optional[bool]): Deprecated. Has the opposite logic for
                `disable_edit_message`.
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            :class:`telegram.Message` or True: The edited message, or if the
                message wasn't sent by the bot, True.

        """
        url = '{0}/setGameScore'.format(self.base_url)

        data = {'user_id': user_id, 'score': score}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if force is not None:
            data['force'] = force
        if disable_edit_message is not None:
            data['disable_edit_message'] = disable_edit_message
        if edit_message is not None:
            warnings.warn('edit_message is deprecated, use disable_edit_message instead')
            if disable_edit_message is None:
                data['edit_message'] = edit_message
            else:
                warnings.warn('edit_message is ignored when disable_edit_message is used')

        result = self._request.post(url, data, timeout=timeout)
        if result is True:
            return result
        else:
            return Message.de_json(result, self)

    def getGameHighScores(self,
                          user_id,
                          chat_id=None,
                          message_id=None,
                          inline_message_id=None,
                          timeout=None,
                          **kwargs):
        """Use this method to get data for high score tables.

        Args:
            timeout (Optional[int|float]): If this value is specified, use it as the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).

        Returns:
            list[:class:`telegram.GameHighScore`]: Scores of the specified user and several of his
                neighbors in a game.

        """
        url = '{0}/setGameScore'.format(self.base_url)

        data = {'user_id': user_id}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        result = self._request.post(url, data, timeout=timeout)

        return [GameHighScore.de_json(hs, self) for hs in result]

    @staticmethod
    def de_json(data, bot):
        data = super(Bot, Bot).de_json(data, bot)

        return Bot(**data)

    def to_dict(self):
        data = {'id': self.id, 'username': self.username, 'first_name': self.username}

        if self.last_name:
            data['last_name'] = self.last_name

        return data

    def __reduce__(self):
        return (self.__class__, (self.token, self.base_url.replace(self.token, ''),
                                 self.base_file_url.replace(self.token, '')))

# snake_case (PEP8) aliases

    get_me = getMe
    send_message = sendMessage
    forward_message = forwardMessage
    send_photo = sendPhoto
    send_audio = sendAudio
    send_document = sendDocument
    send_sticker = sendSticker
    send_video = sendVideo
    send_voice = sendVoice
    send_location = sendLocation
    send_venue = sendVenue
    send_contact = sendContact
    send_game = sendGame
    send_chat_action = sendChatAction
    answer_inline_query = answerInlineQuery
    get_user_profile_photos = getUserProfilePhotos
    get_file = getFile
    kick_chat_member = kickChatMember
    unban_chat_member = unbanChatMember
    answer_callback_query = answerCallbackQuery
    edit_message_text = editMessageText
    edit_message_caption = editMessageCaption
    edit_message_reply_markup = editMessageReplyMarkup
    get_updates = getUpdates
    set_webhook = setWebhook
    delete_webhook = deleteWebhook
    leave_chat = leaveChat
    get_chat = getChat
    get_chat_administrators = getChatAdministrators
    get_chat_member = getChatMember
    get_chat_members_count = getChatMembersCount
    get_webhook_info = getWebhookInfo
    set_game_score = setGameScore
    get_game_high_scores = getGameHighScores
