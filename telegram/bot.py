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
"""This module contains a object that represents a Telegram Bot."""

import logging
import functools

from telegram import (User, Message, Update, UserProfilePhotos, File, ReplyMarkup, TelegramObject,
                      NullHandler)
from telegram.utils import request
from telegram.utils.validate import validate_token

logging.getLogger(__name__).addHandler(NullHandler())


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

    """

    def __init__(self, token, base_url=None, base_file_url=None):
        self.token = validate_token(token)

        if not base_url:
            self.base_url = 'https://api.telegram.org/bot{0}'.format(self.token)
        else:
            self.base_url = base_url + self.token

        if not base_file_url:
            self.base_file_url = 'https://api.telegram.org/file/bot{0}'.format(self.token)
        else:
            self.base_file_url = base_file_url + self.token

        self.bot = None

        self.logger = logging.getLogger(__name__)

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

            result = request.post(url, data, timeout=kwargs.get('timeout'))

            if result is True:
                return result

            return Message.de_json(result)

        return decorator

    @log
    def getMe(self):
        """A simple method for testing your bot's auth token.

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance
            representing that bot if the credentials are valid, `None`
            otherwise.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/getMe'.format(self.base_url)

        result = request.get(url)

        self.bot = User.de_json(result)

        return self.bot

    @log
    @message
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, **kwargs):
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
            **kwargs (dict): Arbitrary keyword arguments.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, the sent message is
            returned.

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
    def forwardMessage(self, chat_id, from_chat_id, message_id, **kwargs):
        """Use this method to forward messages of any kind.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          from_chat_id:
            Unique identifier for the chat where the original message was sent
            - Chat id.
          message_id:
            Unique message identifier.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message forwarded.

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
    def sendPhoto(self, chat_id, photo, caption=None, **kwargs):
        """Use this method to send photos.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          photo:
            Photo to send. You can either pass a file_id as String to resend a
            photo that is already on the Telegram servers, or upload a new
            photo using multipart/form-data.
          caption:
            Photo caption (may also be used when resending photos by file_id).
            [Optional]

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

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
    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, **kwargs):
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
            Unique identifier for the message recipient - Chat id.
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

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

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

        return url, data

    @log
    @message
    def sendDocument(self, chat_id, document, filename=None, caption=None, **kwargs):
        """Use this method to send general files.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          document:
            File to send. You can either pass a file_id as String to resend a
            file that is already on the Telegram servers, or upload a new file
            using multipart/form-data.
          filename:
            File name that shows in telegram message (it is usefull when you
            send file generated by temp module, for example). [Optional]
          caption:
            Document caption (may also be used when resending documents by
            file_id), 0-200 characters. [Optional]

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

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
    def sendSticker(self, chat_id, sticker, **kwargs):
        """Use this method to send .webp stickers.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          sticker:
            Sticker to send. You can either pass a file_id as String to resend
            a sticker that is already on the Telegram servers, or upload a new
            sticker using multipart/form-data.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/sendSticker'.format(self.base_url)

        data = {'chat_id': chat_id, 'sticker': sticker}

        return url, data

    @log
    @message
    def sendVideo(self, chat_id, video, duration=None, caption=None, **kwargs):
        """Use this method to send video files, Telegram clients support mp4
        videos (other formats may be sent as telegram.Document).

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          video:
            Video to send. You can either pass a file_id as String to resend a
            video that is already on the Telegram servers, or upload a new
            video file using multipart/form-data.
          duration:
            Duration of sent video in seconds. [Optional]
          caption:
            Video caption (may also be used when resending videos by file_id).
            [Optional]

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

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
    def sendVoice(self, chat_id, voice, duration=None, **kwargs):
        """Use this method to send audio files, if you want Telegram clients to
        display the file as a playable voice message. For this to work, your
        audio must be in an .ogg file encoded with OPUS (other formats may be
        sent as Audio or Document). On success, the sent Message is returned.
        Bots can currently send audio files of up to 50 MB in size, this limit
        may be changed in the future.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          voice:
            Audio file to send. You can either pass a file_id as String to
            resend an audio that is already on the Telegram servers, or upload
            a new audio file using multipart/form-data.
          duration:
            Duration of sent audio in seconds. [Optional]

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/sendVoice'.format(self.base_url)

        data = {'chat_id': chat_id, 'voice': voice}

        if duration:
            data['duration'] = duration

        return url, data

    @log
    @message
    def sendLocation(self, chat_id, latitude, longitude, **kwargs):
        """Use this method to send point on the map.

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
          latitude:
            Latitude of location.
          longitude:
            Longitude of location.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/sendLocation'.format(self.base_url)

        data = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude}

        return url, data

    @log
    @message
    def sendVenue(
            self, chat_id,
            latitude,
            longitude,
            title, address,
            foursquare_id=None,
            **kwargs):
        """
        Use this method to send information about a venue.

        Args:
            chat_id:
                Unique identifier for the target chat or username of the target
                channel (in the format @channelusername).
            latitude:
                Latitude of the venue.
            longitude:
                Longitude of the venue.
            title:
                Name of the venue.
            address:
                Address of the venue.
            foursquare_id:
                Foursquare identifier of the venue.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/sendVenue'.format(self.base_url)

        data = {'chat_id': chat_id,
                'latitude': latitude,
                'longitude': longitude,
                'address': address,
                'title': title}

        if foursquare_id:
            data['foursquare_id'] = foursquare_id

        return url, data

    @log
    @message
    def sendContact(self, chat_id, phone_number, first_name, last_name=None, **kwargs):
        """
        Use this method to send phone contacts.

        Args:
            chat_id:
                Unique identifier for the target chat or username of the target
                channel (in the format @channelusername).
            phone_number:
                Contact's phone number.
            first_name:
                Contact's first name.
            last_name:
                Contact's last name.

        Keyword Args:
            disable_notification (Optional[bool]): Sends the message silently.
                iOS users will not receive a notification, Android users will
                receive a notification with no sound.
            reply_to_message_id (Optional[int]): If the message is a reply,
                ID of the original message.
            reply_markup (Optional[:class:`telegram.ReplyMarkup`]): Additional
                interface options. A JSON-serialized object for an inline
                keyboard, custom reply keyboard, instructions to hide reply
                keyboard or to force a reply from the user.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, instance representing the
            message posted.

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
    def sendChatAction(self, chat_id, action, **kwargs):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its
        typing status).

        Args:
          chat_id:
            Unique identifier for the message recipient - Chat id.
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
                          **kwargs):
        """Use this method to send answers to an inline query. No more than
        50 results per query are allowed.

        Args:
            inline_query_id (str): Unique identifier for the answered query.
            results (list[:class:`telegram.InlineQueryResult`]): A list of
                results for the inline query.
            cache_time (Optional[int]): The maximum amount of time the
                result of the inline query may be cached on the server.
            is_personal (Optional[bool]): Pass `True`, if results may be
                cached on the server side only for the user that sent the
                query. By default, results may be returned to any user who
                sends the same query.
            next_offset (Optional[str]): Pass the offset that a client
                should send in the next query with the same text to receive
                more results. Pass an empty string if there are no more
                results or if you don't support pagination. Offset length
                can't exceed 64 bytes.
            switch_pm_text (Optional[str]): If passed, clients will display
                a button with specified text that switches the user to a
                private chat with the bot and sends the bot a start message
                with the parameter switch_pm_parameter.
            switch_pm_parameter (Optional[str]): Parameter for the start
                message sent to the bot when user presses the switch button.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

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

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return result

    @log
    def getUserProfilePhotos(self, user_id, offset=None, limit=100, **kwargs):
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

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            list[:class:`telegram.UserProfilePhotos`]: A list of
            :class:`telegram.UserProfilePhotos` objects are returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/getUserProfilePhotos'.format(self.base_url)

        data = {'user_id': user_id}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return UserProfilePhotos.de_json(result)

    @log
    def getFile(self, file_id, **kwargs):
        """Use this method to get basic info about a file and prepare it for
        downloading. For the moment, bots can download files of up to 20MB in
        size.

        Args:
          file_id:
            File identifier to get info about.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.File`: On success, a :class:`telegram.File`
            object is returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/getFile'.format(self.base_url)

        data = {'file_id': file_id}

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        if result.get('file_path'):
            result['file_path'] = '%s/%s' % (self.base_file_url, result['file_path'])

        return File.de_json(result)

    @log
    def kickChatMember(self, chat_id, user_id, **kwargs):
        """Use this method to kick a user from a group or a supergroup. In the
        case of supergroups, the user will not be able to return to the group
        on their own using invite links, etc., unless unbanned first. The bot
        must be an administrator in the group for this to work.

        Args:
          chat_id:
            Unique identifier for the target group or username of the target
            supergroup (in the format @supergroupusername).
          user_id:
            Unique identifier of the target user.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/kickChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return result

    @log
    def unbanChatMember(self, chat_id, user_id, **kwargs):
        """Use this method to unban a previously kicked user in a supergroup.
        The user will not return to the group automatically, but will be able
        to join via link, etc. The bot must be an administrator in the group
        for this to work.

        Args:
          chat_id:
            Unique identifier for the target group or username of the target
            supergroup (in the format @supergroupusername).
          user_id:
            Unique identifier of the target user.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/unbanChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return result

    @log
    def answerCallbackQuery(self, callback_query_id, text=None, show_alert=False, **kwargs):
        """Use this method to send answers to callback queries sent from
        inline keyboards. The answer will be displayed to the user as a
        notification at the top of the chat screen or as an alert.

        Args:
            callback_query_id (str): Unique identifier for the query to be
                answered.
            text (Optional[str]): Text of the notification. If not
                specified, nothing will be shown to the user.
            show_alert (Optional[bool]): If `True`, an alert will be shown
                by the client instead of a notification at the top of the chat
                screen. Defaults to `False`.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.
            network_delay (Optional[float]): If using the timeout (which is
                a `timeout` for the Telegram servers operation),
                then `network_delay` as an extra delay (in seconds) to
                compensate for network latency. Defaults to 2.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/answerCallbackQuery'.format(self.base_url)

        data = {'callback_query_id': callback_query_id}

        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return result

    @log
    def editMessageText(self,
                        text,
                        chat_id=None,
                        message_id=None,
                        inline_message_id=None,
                        parse_mode=None,
                        disable_web_page_preview=None,
                        reply_markup=None,
                        **kwargs):
        """Use this method to edit text messages sent by the bot or via the bot
        (for inline bots).

        Args:
          text:
            New text of the message.
          chat_id:
            Required if inline_message_id is not specified. Unique identifier
            for the target chat or username of the target channel (in the
            format @channelusername).
          message_id:
            Required if inline_message_id is not specified. Unique identifier
            of the sent message.
          inline_message_id:
            Required if chat_id and message_id are not specified. Identifier of
            the inline message.
          parse_mode:
            Send Markdown or HTML, if you want Telegram apps to show bold,
            italic, fixed-width text or inline URLs in your bot's message.
          disable_web_page_preview:
            Disables link previews for links in this message.
          reply_markup:
            A JSON-serialized object for an inline keyboard.

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by
            the bot, the edited message is returned, otherwise `True` is
            returned.

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
        if reply_markup:
            if isinstance(reply_markup, ReplyMarkup):
                data['reply_markup'] = reply_markup.to_json()
            else:
                data['reply_markup'] = reply_markup

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return Message.de_json(result)

    @log
    @message
    def editMessageCaption(self,
                           chat_id=None,
                           message_id=None,
                           inline_message_id=None,
                           caption=None,
                           **kwargs):
        """Use this method to edit captions of messages sent by the bot or
        via the bot (for inline bots).

        Args:
            chat_id (Optional[str]): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of
                the target channel (in the format @channelusername).
            message_id (Optional[str]): Required if inline_message_id is not
                specified. Unique identifier of the sent message.
            inline_message_id (Optional[str]): Required if chat_id and
                message_id are not specified. Identifier of the inline message.
            caption (Optional[str]): New caption of the message.
            **kwargs (Optional[dict]): Arbitrary keyword arguments.

        Keyword Args:
            reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
                A JSON-serialized object for an inline keyboard.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by
            the bot, the edited message is returned, otherwise `True` is
            returned.

        Raises:
            :class:`telegram.TelegramError`

        """

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
    def editMessageReplyMarkup(
            self, chat_id=None,
            message_id=None, inline_message_id=None,
            **kwargs):
        """Use this method to edit only the reply markup of messages sent by
        the bot or via the bot (for inline bots).

        Args:
            chat_id (Optional[str]): Required if inline_message_id is not
                specified. Unique identifier for the target chat or username of
                the target channel (in the format @channelusername).
            message_id (Optional[str]): Required if inline_message_id is not
                specified. Unique identifier of the sent message.
            inline_message_id (Optional[str]): Required if chat_id and
                message_id are not specified. Identifier of the inline message.
            **kwargs (Optional[dict]): Arbitrary keyword arguments.

        Keyword Args:
            reply_markup (Optional[:class:`telegram.InlineKeyboardMarkup`]):
                A JSON-serialized object for an inline keyboard.
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by
            the bot, the edited message is returned, otherwise `True` is
            returned.

        Raises:
            :class:`telegram.TelegramError`

        """

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
    def getUpdates(self, offset=None, limit=100, timeout=0, network_delay=.2):
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
            list[:class:`telegram.Update`]: A list of :class:`telegram.Update`
            objects are returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/getUpdates'.format(self.base_url)

        data = {'timeout': timeout}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        urlopen_timeout = timeout + network_delay

        result = request.post(url, data, timeout=urlopen_timeout)

        if result:
            self.logger.debug('Getting updates: %s', [u['update_id'] for u in result])
        else:
            self.logger.debug('No new updates found.')

        return [Update.de_json(x) for x in result]

    @log
    def setWebhook(self, webhook_url=None, certificate=None, **kwargs):
        """Use this method to specify a url and receive incoming updates via an
        outgoing webhook. Whenever there is an update for the bot, we will send
        an HTTPS POST request to the specified url, containing a
        JSON-serialized Update. In case of an unsuccessful request, we will
        give up after a reasonable amount of attempts.

        Args:
          webhook_url:
            HTTPS url to send updates to.
            Use an empty string to remove webhook integration

        Keyword Args:
            timeout (Optional[float]): If this value is specified, use it as
                the definitive timeout (in seconds) for urlopen() operations.

        Returns:
            bool: On success, `True` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """

        url = '{0}/setWebhook'.format(self.base_url)

        data = {}

        if webhook_url is not None:
            data['url'] = webhook_url
        if certificate:
            data['certificate'] = certificate

        result = request.post(url, data, timeout=kwargs.get('timeout'))

        return result

    @staticmethod
    def de_json(data):
        data = super(Bot, Bot).de_json(data)

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
