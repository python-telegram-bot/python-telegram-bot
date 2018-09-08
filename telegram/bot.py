#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2018
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
try:
    import ujson as json
except ImportError:
    import json
import logging
import warnings
from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from future.utils import string_types

from telegram import (User, Message, Update, Chat, ChatMember, UserProfilePhotos, File,
                      ReplyMarkup, TelegramObject, WebhookInfo, GameHighScore, StickerSet,
                      PhotoSize, Audio, Document, Sticker, Video, Animation, Voice, VideoNote,
                      Location, Venue, Contact, InputFile)
from telegram.error import InvalidToken, TelegramError
from telegram.utils.helpers import to_timestamp
from telegram.utils.request import Request

logging.getLogger(__name__).addHandler(logging.NullHandler())


def info(func):
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        if not self.bot:
            self.get_me()

        result = func(self, *args, **kwargs)
        return result

    return decorator


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


class Bot(TelegramObject):
    """This object represents a Telegram Bot.

    Args:
        token (:obj:`str`): Bot's unique authentication.
        base_url (:obj:`str`, optional): Telegram Bot API service URL.
        base_file_url (:obj:`str`, optional): Telegram Bot API file URL.
        request (:obj:`telegram.utils.request.Request`, optional): Pre initialized
            :obj:`telegram.utils.request.Request`.
        private_key (:obj:`bytes`, optional): Private key for decryption of telegram passport data.
        private_key_password (:obj:`bytes`, optional): Password for above private key.

    """

    def __init__(self, token, base_url=None, base_file_url=None, request=None, private_key=None,
                 private_key_password=None):
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

        if private_key:
            self.private_key = serialization.load_pem_private_key(private_key,
                                                                  password=private_key_password,
                                                                  backend=default_backend())

    @property
    def request(self):
        return self._request

    @staticmethod
    def _validate_token(token):
        """A very basic validation on token."""
        if any(x.isspace() for x in token):
            raise InvalidToken()

        left, sep, _right = token.partition(':')
        if (not sep) or (not left.isdigit()) or (len(left) < 3):
            raise InvalidToken()

        return token

    @property
    @info
    def id(self):
        """:obj:`int`: Unique identifier for this bot."""

        return self.bot.id

    @property
    @info
    def first_name(self):
        """:obj:`str`: Bot's first name."""

        return self.bot.first_name

    @property
    @info
    def last_name(self):
        """:obj:`str`: Optional. Bot's last name."""

        return self.bot.last_name

    @property
    @info
    def username(self):
        """:obj:`str`: Bot's username."""

        return self.bot.username

    @property
    def name(self):
        """:obj:`str`: Bot's @username."""

        return '@{0}'.format(self.username)

    @log
    def get_me(self, timeout=None, **kwargs):
        """A simple method for testing your bot's auth token. Requires no parameters.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
            :class:`telegram.User`: A :class:`telegram.User` instance representing that bot if the
            credentials are valid, :obj:`None` otherwise.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getMe'.format(self.base_url)

        result = self._request.get(url, timeout=timeout)

        self.bot = User.de_json(result, self)

        return self.bot

    @log
    @message
    def send_message(self,
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
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            text (:obj:`str`): Text of the message to be sent. Max 4096 characters. Also found as
                :attr:`telegram.constants.MAX_MESSAGE_LENGTH`.
            parse_mode (:obj:`str`): Send Markdown or HTML, if you want Telegram apps to show bold,
                italic, fixed-width text or inline URLs in your bot's message. See the constants in
                :class:`telegram.ParseMode` for the available modes.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options.
                A JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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
    def delete_message(self, chat_id, message_id, timeout=None, **kwargs):
        """
        Use this method to delete a message. A message can only be deleted if it was sent less
        than 48 hours ago. Any such recently sent outgoing message may be deleted. Additionally,
        if the bot is an administrator in a group chat, it can delete any message. If the bot is
        an administrator in a supergroup, it can delete messages from any other user and service
        messages about people joining or leaving the group (other types of service messages may
        only be removed by the group creator). In channels, bots can only remove their own
        messages.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            message_id (:obj:`int`): Identifier of the message to delete.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
            the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/deleteMessage'.format(self.base_url)

        data = {'chat_id': chat_id, 'message_id': message_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    @message
    def forward_message(self,
                        chat_id,
                        from_chat_id,
                        message_id,
                        disable_notification=False,
                        timeout=None,
                        **kwargs):
        """Use this method to forward messages of any kind.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            from_chat_id (:obj:`int` | :obj:`str`): Unique identifier for the chat where the
                original message was sent (or channel username in the format @channelusername).
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            message_id (:obj:`int`): Message identifier in the chat specified in from_chat_id.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
            the read timeout
                from the server (instead of the one specified during creation of the connection
                pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

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
    def send_photo(self,
                   chat_id,
                   photo,
                   caption=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=20,
                   parse_mode=None,
                   **kwargs):
        """Use this method to send photos.

        Note:
            The photo argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            photo (:obj:`str` | `filelike object` | :class:`telegram.PhotoSize`): Photo to send.
                Pass a file_id as String to send a photo that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a photo from the
                Internet, or upload a new photo using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.PhotoSize` object to send.
            caption (:obj:`str`, optional): Photo caption (may also be used when resending photos
                by file_id), 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendPhoto'.format(self.base_url)

        if isinstance(photo, PhotoSize):
            photo = photo.file_id
        elif InputFile.is_file(photo):
            photo = InputFile(photo)

        data = {'chat_id': chat_id, 'photo': photo}

        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode

        return url, data

    @log
    @message
    def send_audio(self,
                   chat_id,
                   audio,
                   duration=None,
                   performer=None,
                   title=None,
                   caption=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=20,
                   parse_mode=None,
                   thumb=None,
                   **kwargs):
        """
        Use this method to send audio files, if you want Telegram clients to display them in the
        music player. Your audio must be in the .mp3 format. On success, the sent Message is
        returned. Bots can currently send audio files of up to 50 MB in size, this limit may be
        changed in the future.

        For sending voice messages, use the sendVoice method instead.

        Note:
            The audio argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            audio (:obj:`str` | `filelike object` | :class:`telegram.Audio`): Audio file to send.
                Pass a file_id as String to send an audio file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an audio file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Audio` object to send.
            caption (:obj:`str`, optional): Audio caption, 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            duration (:obj:`int`, optional): Duration of sent audio in seconds.
            performer (:obj:`str`, optional): Performer.
            title (:obj:`str`, optional): Track name.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object`, optional): Thumbnail of the
                file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
                A thumbnail's width and height should not exceed 90. Ignored if the file is not
                is passed as a string or file_id.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendAudio'.format(self.base_url)

        if isinstance(audio, Audio):
            audio = audio.file_id
        elif InputFile.is_file(audio):
            audio = InputFile(audio)

        data = {'chat_id': chat_id, 'audio': audio}

        if duration:
            data['duration'] = duration
        if performer:
            data['performer'] = performer
        if title:
            data['title'] = title
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if thumb:
            if InputFile.is_file(thumb):
                thumb = InputFile(thumb, attach=True)
            data['thumb'] = thumb

        return url, data

    @log
    @message
    def send_document(self,
                      chat_id,
                      document,
                      filename=None,
                      caption=None,
                      disable_notification=False,
                      reply_to_message_id=None,
                      reply_markup=None,
                      timeout=20,
                      parse_mode=None,
                      thumb=None,
                      **kwargs):
        """Use this method to send general files.

        Note:
            The document argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            document (:obj:`str` | `filelike object` | :class:`telegram.Document`): File to send.
                Pass a file_id as String to send a file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a file from the
                Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Document` object to send.
            filename (:obj:`str`, optional): File name that shows in telegram message (it is useful
                when you send file generated by temp module, for example). Undocumented.
            caption (:obj:`str`, optional): Document caption (may also be used when resending
                documents by file_id), 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object`, optional): Thumbnail of the
                file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
                A thumbnail's width and height should not exceed 90. Ignored if the file is not
                is passed as a string or file_id.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendDocument'.format(self.base_url)

        if isinstance(document, Document):
            document = document.file_id
        elif InputFile.is_file(document):
            document = InputFile(document, filename=filename)

        data = {'chat_id': chat_id, 'document': document}

        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if thumb:
            if InputFile.is_file(thumb):
                thumb = InputFile(thumb, attach=True)
            data['thumb'] = thumb

        return url, data

    @log
    @message
    def send_sticker(self,
                     chat_id,
                     sticker,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=20,
                     **kwargs):
        """Use this method to send .webp stickers.

        Note:
            The sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            sticker (:obj:`str` | `filelike object` :class:`telegram.Sticker`): Sticker to send.
                Pass a file_id as String to send a file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get a .webp file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Sticker` object to send.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendSticker'.format(self.base_url)

        if isinstance(sticker, Sticker):
            sticker = sticker.file_id
        elif InputFile.is_file(sticker):
            sticker = InputFile(sticker)

        data = {'chat_id': chat_id, 'sticker': sticker}

        return url, data

    @log
    @message
    def send_video(self,
                   chat_id,
                   video,
                   duration=None,
                   caption=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=20,
                   width=None,
                   height=None,
                   parse_mode=None,
                   supports_streaming=None,
                   thumb=None,
                   **kwargs):
        """
        Use this method to send video files, Telegram clients support mp4 videos
        (other formats may be sent as Document).

        Note:
            The video argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            video (:obj:`str` | `filelike object` | :class:`telegram.Video`): Video file to send.
                Pass a file_id as String to send an video file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an video file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Video` object to send.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            width (:obj:`int`, optional): Video width.
            height (:obj:`int`, optional): Video height.
            caption (:obj:`str`, optional): Video caption (may also be used when resending videos
                by file_id), 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            supports_streaming (:obj:`bool`, optional): Pass True, if the uploaded video is
                suitable for streaming.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object`, optional): Thumbnail of the
                file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
                A thumbnail's width and height should not exceed 90. Ignored if the file is not
                is passed as a string or file_id.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVideo'.format(self.base_url)

        if isinstance(video, Video):
            video = video.file_id
        elif InputFile.is_file(video):
            video = InputFile(video)

        data = {'chat_id': chat_id, 'video': video}

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if supports_streaming:
            data['supports_streaming'] = supports_streaming
        if width:
            data['width'] = width
        if height:
            data['height'] = height
        if thumb:
            if InputFile.is_file(thumb):
                thumb = InputFile(thumb, attach=True)
            data['thumb'] = thumb

        return url, data

    @log
    @message
    def send_video_note(self,
                        chat_id,
                        video_note,
                        duration=None,
                        length=None,
                        disable_notification=False,
                        reply_to_message_id=None,
                        reply_markup=None,
                        timeout=20,
                        thumb=None,
                        **kwargs):
        """Use this method to send video messages.

        Note:
            The video_note argument can be either a file_id or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            video_note (:obj:`str` | `filelike object` | :class:`telegram.VideoNote`): Video note
                to send. Pass a file_id as String to send a video note that exists on the Telegram
                servers (recommended) or upload a new video using multipart/form-data. Or you can
                pass an existing :class:`telegram.VideoNote` object to send. Sending video notes by
                a URL is currently unsupported.
            duration (:obj:`int`, optional): Duration of sent video in seconds.
            length (:obj:`int`, optional): Video width and height
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            thumb (`filelike object`, optional): Thumbnail of the
                file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
                A thumbnail's width and height should not exceed 90. Ignored if the file is not
                is passed as a string or file_id.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVideoNote'.format(self.base_url)

        if isinstance(video_note, VideoNote):
            video_note = video_note.file_id
        elif InputFile.is_file(video_note):
            video_note = InputFile(video_note)

        data = {'chat_id': chat_id, 'video_note': video_note}

        if duration is not None:
            data['duration'] = duration
        if length is not None:
            data['length'] = length
        if thumb:
            if InputFile.is_file(thumb):
                thumb = InputFile(thumb, attach=True)
            data['thumb'] = thumb

        return url, data

    @log
    @message
    def send_animation(self,
                       chat_id,
                       animation,
                       duration=None,
                       width=None,
                       height=None,
                       thumb=None,
                       caption=None,
                       parse_mode=None,
                       disable_notification=False,
                       reply_to_message_id=None,
                       reply_markup=None,
                       timeout=20,
                       **kwargs):
        """
        Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            animation (:obj:`str` | `filelike object` | :class:`telegram.Animation`): Animation to
                send. Pass a file_id as String to send an animation that exists on the Telegram
                servers (recommended), pass an HTTP URL as a String for Telegram to get an
                animation from the Internet, or upload a new animation using multipart/form-data.
                Lastly you can pass an existing :class:`telegram.Animation` object to send.
            duration (:obj:`int`, optional): Duration of sent animation in seconds.
            width (:obj:`int`, optional): Animation width.
            height (:obj:`int`, optional): Animation height.
            thumb (`filelike object`, optional): Thumbnail of the
                file sent. The thumbnail should be in JPEG format and less than 200 kB in size.
                A thumbnail's width and height should not exceed 90. Ignored if the file is not
                is passed as a string or file_id.
            caption (:obj:`str`, optional): Animation caption (may also be used when resending
                animations by file_id), 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendAnimation'.format(self.base_url)

        if isinstance(animation, Animation):
            animation = animation.file_id
        elif InputFile.is_file(animation):
            animation = InputFile(animation)

        data = {'chat_id': chat_id, 'animation': animation}

        if duration:
            data['duration'] = duration
        if width:
            data['width'] = width
        if height:
            data['height'] = height
        if thumb:
            if InputFile.is_file(thumb):
                thumb = InputFile(thumb, attach=True)
            data['thumb'] = thumb
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode

        return url, data

    @log
    @message
    def send_voice(self,
                   chat_id,
                   voice,
                   duration=None,
                   caption=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=20,
                   parse_mode=None,
                   **kwargs):
        """
        Use this method to send audio files, if you want Telegram clients to display the file
        as a playable voice message. For this to work, your audio must be in an .ogg file
        encoded with OPUS (other formats may be sent as Audio or Document).

        Note:
            The voice argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            voice (:obj:`str` | `filelike object` | :class:`telegram.Voice`): Voice file to send.
                Pass a file_id as String to send an voice file that exists on the Telegram servers
                (recommended), pass an HTTP URL as a String for Telegram to get an voice file from
                the Internet, or upload a new one using multipart/form-data. Lastly you can pass
                an existing :class:`telegram.Voice` object to send.
            caption (:obj:`str`, optional): Voice message caption, 0-200 characters.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            duration (:obj:`int`, optional): Duration of the voice message in seconds.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVoice'.format(self.base_url)

        if isinstance(voice, Voice):
            voice = voice.file_id
        elif InputFile.is_file(voice):
            voice = InputFile(voice)

        data = {'chat_id': chat_id, 'voice': voice}

        if duration:
            data['duration'] = duration
        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode

        return url, data

    @log
    def send_media_group(self,
                         chat_id,
                         media,
                         disable_notification=None,
                         reply_to_message_id=None,
                         timeout=20,
                         **kwargs):
        """Use this method to send a group of photos or videos as an album.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            media (List[:class:`telegram.InputMedia`]): An array describing photos and videos to be
                sent, must include 2–10 items.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            timeout (:obj:`int` | :obj:`float`, optional): Send file timeout (default: 20 seconds).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            List[:class:`telegram.Message`]: An array of the sent Messages.

        Raises:
            :class:`telegram.TelegramError`
        """

        url = '{0}/sendMediaGroup'.format(self.base_url)

        data = {'chat_id': chat_id, 'media': media}

        if reply_to_message_id:
            data['reply_to_message_id'] = reply_to_message_id
        if disable_notification:
            data['disable_notification'] = disable_notification

        result = self._request.post(url, data, timeout=timeout)

        return [Message.de_json(res, self) for res in result]

    @log
    @message
    def send_location(self,
                      chat_id,
                      latitude=None,
                      longitude=None,
                      disable_notification=False,
                      reply_to_message_id=None,
                      reply_markup=None,
                      timeout=None,
                      location=None,
                      live_period=None,
                      **kwargs):
        """Use this method to send point on the map.

        Note:
            You can either supply a :obj:`latitude` and :obj:`longitude` or a :obj:`location`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            location (:class:`telegram.Location`, optional): The location to send.
            live_period (:obj:`int`, optional): Period in seconds for which the location will be
                updated, should be between 60 and 86400.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                    original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendLocation'.format(self.base_url)

        if not (all([latitude, longitude]) or location):
            raise ValueError("Either location or latitude and longitude must be passed as"
                             "argument.")

        if not ((latitude is not None or longitude is not None) ^ bool(location)):
            raise ValueError("Either location or latitude and longitude must be passed as"
                             "argument. Not both.")

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude}

        if live_period:
            data['live_period'] = live_period

        return url, data

    @log
    @message
    def edit_message_live_location(self,
                                   chat_id=None,
                                   message_id=None,
                                   inline_message_id=None,
                                   latitude=None,
                                   longitude=None,
                                   location=None,
                                   reply_markup=None,
                                   **kwargs):
        """Use this method to edit live location messages sent by the bot or via the bot
        (for inline bots). A location can be edited until its :attr:`live_period` expires or
        editing is explicitly disabled by a call to :attr:`stop_message_live_location`.

        Note:
            You can either supply a :obj:`latitude` and :obj:`longitude` or a :obj:`location`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            latitude (:obj:`float`, optional): Latitude of location.
            longitude (:obj:`float`, optional): Longitude of location.
            location (:class:`telegram.Location`, optional): The location to send.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
             :class:`telegram.Message`: On success the edited message.
        """

        url = '{0}/editMessageLiveLocation'.format(self.base_url)

        if not (all([latitude, longitude]) or location):
            raise ValueError("Either location or latitude and longitude must be passed as"
                             "argument.")
        if not ((latitude is not None or longitude is not None) ^ bool(location)):
            raise ValueError("Either location or latitude and longitude must be passed as"
                             "argument. Not both.")

        if isinstance(location, Location):
            latitude = location.latitude
            longitude = location.longitude

        data = {'latitude': latitude, 'longitude': longitude}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    @message
    def stop_message_live_location(self,
                                   chat_id=None,
                                   message_id=None,
                                   inline_message_id=None,
                                   reply_markup=None,
                                   **kwargs):
        """Use this method to stop updating a live location message sent by the bot or via the bot
        (for inline bots) before live_period expires.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).

        Returns:
            :class:`telegram.Message`: On success the edited message.
        """

        url = '{0}/stopMessageLiveLocation'.format(self.base_url)

        data = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    @message
    def send_venue(self,
                   chat_id,
                   latitude=None,
                   longitude=None,
                   title=None,
                   address=None,
                   foursquare_id=None,
                   disable_notification=False,
                   reply_to_message_id=None,
                   reply_markup=None,
                   timeout=None,
                   venue=None,
                   foursquare_type=None,
                   **kwargs):
        """Use this method to send information about a venue.

        Note:
            you can either supply :obj:`venue`, or :obj:`latitude`, :obj:`longitude`,
            :obj:`title` and :obj:`address` and optionally :obj:`foursquare_id` and optionally
            :obj:`foursquare_type`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            latitude (:obj:`float`, optional): Latitude of venue.
            longitude (:obj:`float`, optional): Longitude of venue.
            title (:obj:`str`, optional): Name of the venue.
            address (:obj:`str`, optional): Address of the venue.
            foursquare_id (:obj:`str`, optional): Foursquare identifier of the venue.
            foursquare_type (:obj:`str`, optional): Foursquare type of the venue, if known.
                (For example, "arts_entertainment/default", "arts_entertainment/aquarium" or
                "food/icecream".)
            venue (:class:`telegram.Venue`, optional): The venue to send.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendVenue'.format(self.base_url)

        if not (venue or all([latitude, longitude, address, title])):
            raise ValueError("Either venue or latitude, longitude, address and title must be"
                             "passed as arguments.")

        if isinstance(venue, Venue):
            latitude = venue.location.latitude
            longitude = venue.location.longitude
            address = venue.address
            title = venue.title
            foursquare_id = venue.foursquare_id
            foursquare_type = venue.foursquare_type

        data = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'title': title
        }

        if foursquare_id:
            data['foursquare_id'] = foursquare_id
        if foursquare_type:
            data['foursquare_type'] = foursquare_type

        return url, data

    @log
    @message
    def send_contact(self,
                     chat_id,
                     phone_number=None,
                     first_name=None,
                     last_name=None,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=None,
                     contact=None,
                     vcard=None,
                     **kwargs):
        """Use this method to send phone contacts.

        Note:
            You can either supply :obj:`contact` or :obj:`phone_number` and :obj:`first_name`
            with optionally :obj:`last_name` and optionally :obj:`vcard`.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            phone_number (:obj:`str`, optional): Contact's phone number.
            first_name (:obj:`str`, optional): Contact's first name.
            last_name (:obj:`str`, optional): Contact's last name.
            vcard (:obj:`str`, optional): Additional data about the contact in the form of a vCard,
                0-2048 bytes.
            contact (:class:`telegram.Contact`, optional): The contact to send.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendContact'.format(self.base_url)

        if (not contact) and (not all([phone_number, first_name])):
            raise ValueError("Either contact or phone_number and first_name must be passed as"
                             "arguments.")

        if isinstance(contact, Contact):
            phone_number = contact.phone_number
            first_name = contact.first_name
            last_name = contact.last_name
            vcard = contact.vcard

        data = {'chat_id': chat_id, 'phone_number': phone_number, 'first_name': first_name}

        if last_name:
            data['last_name'] = last_name
        if vcard:
            data['vcard'] = vcard

        return url, data

    @log
    @message
    def send_game(self,
                  chat_id,
                  game_short_name,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        """Use this method to send a game.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            game_short_name (:obj:`str`): Short name of the game, serves as the unique identifier
                for the game. Set up your games via Botfather.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendGame'.format(self.base_url)

        data = {'chat_id': chat_id, 'game_short_name': game_short_name}

        return url, data

    @log
    def send_chat_action(self, chat_id, action, timeout=None, **kwargs):
        """
        Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Telegram clients clear its typing status).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            action(:class:`telegram.ChatAction` | :obj:`str`): Type of action to broadcast. Choose
                one, depending on what the user is about to receive. For convenience look at the
                constants in :class:`telegram.ChatAction`
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendChatAction'.format(self.base_url)

        data = {'chat_id': chat_id, 'action': action}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def answer_inline_query(self,
                            inline_query_id,
                            results,
                            cache_time=300,
                            is_personal=None,
                            next_offset=None,
                            switch_pm_text=None,
                            switch_pm_parameter=None,
                            timeout=None,
                            **kwargs):
        """
        Use this method to send answers to an inline query. No more than 50 results per query are
        allowed.

        Args:
            inline_query_id (:obj:`str`): Unique identifier for the answered query.
            results (List[:class:`telegram.InlineQueryResult`)]: A list of results for the inline
                query.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the inline query may be cached on the server. Defaults to 300.
            is_personal (:obj:`bool`, optional): Pass True, if results may be cached on the server
                side only for the user that sent the query. By default, results may be returned to
                any user who sends the same query.
            next_offset (:obj:`str`, optional): Pass the offset that a client should send in the
                next query with the same text to receive more results. Pass an empty string if
                there are no more results or if you don't support pagination. Offset length can't
                exceed 64 bytes.
            switch_pm_text (:obj:`str`, optional): If passed, clients will display a button with
                specified text that switches the user to a private chat with the bot and sends the
                bot a start message with the parameter switch_pm_parameter.
            switch_pm_parameter (:obj:`str`, optional): Deep-linking parameter for the /start
                message sent to the bot when user presses the switch button. 1-64 characters,
                only A-Z, a-z, 0-9, _ and - are allowed.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                he read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Example:
            An inline bot that sends YouTube videos can ask the user to connect the bot to their
            YouTube account to adapt search results accordingly. To do this, it displays a
            'Connect your YouTube account' button above the results, or even before showing any.
            The user presses the button, switches to a private chat with the bot and, in doing so,
            passes a start parameter that instructs the bot to return an oauth link. Once done, the
            bot can offer a switch_inline button so that the user can easily return to the chat
            where they wanted to use the bot's inline capabilities.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

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

        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def get_user_profile_photos(self, user_id, offset=None, limit=100, timeout=None, **kwargs):
        """Use this method to get a list of profile pictures for a user.

        Args:
            user_id (:obj:`int`): Unique identifier of the target user.
            offset (:obj:`int`, optional): Sequential number of the first photo to be returned.
                By default, all photos are returned.
            limit (:obj:`int`, optional): Limits the number of photos to be retrieved. Values
                between 1-100 are accepted. Defaults to 100.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.UserProfilePhotos`

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getUserProfilePhotos'.format(self.base_url)

        data = {'user_id': user_id}

        if offset is not None:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return UserProfilePhotos.de_json(result, self)

    @log
    def get_file(self, file_id, timeout=None, **kwargs):
        """
        Use this method to get basic info about a file and prepare it for downloading. For the
        moment, bots can download files of up to 20MB in size. The file can then be downloaded
        with :attr:`telegram.File.download`. It is guaranteed that the link will be
        valid for at least 1 hour. When the link expires, a new one can be requested by
        calling get_file again.

        Args:
            file_id (:obj:`str` | :class:`telegram.Audio` | :class:`telegram.Document` |          \
                     :class:`telegram.PhotoSize` | :class:`telegram.Sticker` |                    \
                     :class:`telegram.Video` | :class:`telegram.VideoNote` |                      \
                     :class:`telegram.Voice`):
                Either the file identifier or an object that has a file_id attribute
                to get file information about.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.File`

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getFile'.format(self.base_url)

        try:
            file_id = file_id.file_id
        except AttributeError:
            pass

        data = {'file_id': file_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        if result.get('file_path'):
            result['file_path'] = '%s/%s' % (self.base_file_url, result['file_path'])

        return File.de_json(result, self)

    @log
    def kick_chat_member(self, chat_id, user_id, timeout=None, until_date=None, **kwargs):
        """
        Use this method to kick a user from a group or a supergroup. In the case of supergroups,
        the user will not be able to return to the group on their own using invite links, etc.,
        unless unbanned first. The bot must be an administrator in the group for this to work.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or  username
                of the target channel (in the format @channelusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when the user will
                be unbanned, unix time. If user is banned for more than 366 days or less than 30
                seconds from the current time they are considered to be banned forever.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Note:
            In regular groups (non-supergroups), this method will only work if the
            'All Members Are Admins' setting is off in the target group. Otherwise
            members may only be removed by the group's creator or by the member that added them.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/kickChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}
        data.update(kwargs)

        if until_date is not None:
            if isinstance(until_date, datetime):
                until_date = to_timestamp(until_date)
            data['until_date'] = until_date

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def unban_chat_member(self, chat_id, user_id, timeout=None, **kwargs):
        """Use this method to unban a previously kicked user in a supergroup.

        The user will not return to the group automatically, but will be able to join via link,
        etc. The bot must be an administrator in the group for this to work.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/unbanChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def answer_callback_query(self,
                              callback_query_id,
                              text=None,
                              show_alert=False,
                              url=None,
                              cache_time=None,
                              timeout=None,
                              **kwargs):
        """
        Use this method to send answers to callback queries sent from inline keyboards. The answer
        will be displayed to the user as a notification at the top of the chat screen or as an
        alert.
        Alternatively, the user can be redirected to the specified Game URL. For this option to
        work, you must first create a game for your bot via BotFather and accept the terms.
        Otherwise, you may use links like t.me/your_bot?start=XXXX that open your bot with
        a parameter.

        Args:
            callback_query_id (:obj:`str`): Unique identifier for the query to be answered.
            text (:obj:`str`, optional): Text of the notification. If not specified, nothing will
                be shown to the user, 0-200 characters.
            show_alert (:obj:`bool`, optional): If true, an alert will be shown by the client
                instead of a notification at the top of the chat screen. Defaults to false.
            url (:obj:`str`, optional): URL that will be opened by the user's client. If you have
                created a Game and accepted the conditions via @Botfather, specify the URL that
                opens your game - note that this will only work if the query comes from a callback
                game button. Otherwise, you may use links like t.me/your_bot?start=XXXX that open
                your bot with a parameter.
            cache_time (:obj:`int`, optional): The maximum amount of time in seconds that the
                result of the callback query may be cached client-side. Defaults to 0.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

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
        data.update(kwargs)

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    @message
    def edit_message_text(self,
                          text,
                          chat_id=None,
                          message_id=None,
                          inline_message_id=None,
                          parse_mode=None,
                          disable_web_page_preview=None,
                          reply_markup=None,
                          timeout=None,
                          **kwargs):
        """
        Use this method to edit text and game messages sent by the bot or via the bot (for inline
        bots).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            text (:obj:`str`): New text of the message.
            parse_mode (:obj:`str`): Send Markdown or HTML, if you want Telegram apps to show bold,
                italic, fixed-width text or inline URLs in your bot's message. See the constants in
                :class:`telegram.ParseMode` for the available modes.
            disable_web_page_preview (:obj:`bool`, optional): Disables link previews for links in
                this message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

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
    def edit_message_caption(self,
                             chat_id=None,
                             message_id=None,
                             inline_message_id=None,
                             caption=None,
                             reply_markup=None,
                             timeout=None,
                             parse_mode=None,
                             **kwargs):
        """
        Use this method to edit captions of messages sent by the bot or via the bot
        (for inline bots).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            caption (:obj:`str`, optional): New caption of the message.
            parse_mode (:obj:`str`, optional): Send Markdown or HTML, if you want Telegram apps to
                show bold, italic, fixed-width text or inline URLs in the media caption. See the
                constants in :class:`telegram.ParseMode` for the available modes.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            edited Message is returned, otherwise ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_caption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        url = '{0}/editMessageCaption'.format(self.base_url)

        data = {}

        if caption:
            data['caption'] = caption
        if parse_mode:
            data['parse_mode'] = parse_mode
        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    @message
    def edit_message_media(self,
                           chat_id=None,
                           message_id=None,
                           inline_message_id=None,
                           media=None,
                           reply_markup=None,
                           timeout=None,
                           **kwargs):
        """Use this method to edit audio, document, photo, or video messages. If a message is a
        part of a message album, then it can be edited only to a photo or a video. Otherwise,
        message type can be changed arbitrarily. When inline message is edited, new file can't be
        uploaded. Use previously uploaded file via its file_id or specify a URL. On success, if the
        edited message was sent by the bot, the edited Message is returned, otherwise True is
        returned.

        Args:
            chat_id (:obj:`int` | :obj:`str`, optional): Unique identifier for the target chat or
                username of the target`channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            media (:class:`telegram.InputMedia`): An object for a new media content
                of the message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.
        """

        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_caption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        url = '{0}/editMessageMedia'.format(self.base_url)

        data = {'media': media}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return url, data

    @log
    @message
    def edit_message_reply_markup(self,
                                  chat_id=None,
                                  message_id=None,
                                  inline_message_id=None,
                                  reply_markup=None,
                                  timeout=None,
                                  **kwargs):
        """
        Use this method to edit only the reply markup of messages sent by the bot or via the bot
        (for inline bots).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options. A
                JSON-serialized object for an inline keyboard, custom reply keyboard, instructions
                to remove reply keyboard or to force a reply from the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, if edited message is sent by the bot, the
            editedMessage is returned, otherwise ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        if inline_message_id is None and (chat_id is None or message_id is None):
            raise ValueError(
                'edit_message_reply_markup: Both chat_id and message_id are required when '
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
    def get_updates(self,
                    offset=None,
                    limit=100,
                    timeout=0,
                    read_latency=2.,
                    allowed_updates=None,
                    **kwargs):
        """Use this method to receive incoming updates using long polling.

        Args:
            offset (:obj:`int`, optional): Identifier of the first update to be returned. Must be
                greater by one than the highest among the identifiers of previously received
                updates. By default, updates starting with the earliest unconfirmed update are
                returned. An update is considered confirmed as soon as getUpdates is called with an
                offset higher than its update_id. The negative offset can be specified to retrieve
                updates starting from -offset update from the end of the updates queue. All
                previous updates will forgotten.
            limit (:obj:`int`, optional): Limits the number of updates to be retrieved. Values
                between 1-100 are accepted. Defaults to 100.
            timeout (:obj:`int`, optional): Timeout in seconds for long polling. Defaults to 0,
                i.e. usual short polling. Should be positive, short polling should be used for
                testing purposes only.
            allowed_updates (List[:obj:`str`]), optional): List the types of updates you want your
                bot to receive. For example, specify ["message", "edited_channel_post",
                "callback_query"] to only receive updates of these types. See
                :class:`telegram.Update` for a complete list of available update types.
                Specify an empty list to receive all updates regardless of type (default). If not
                specified, the previous setting will be used. Please note that this parameter
                doesn't affect updates created before the call to the get_updates, so unwanted
                updates may be received for a short period of time.
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Notes:
            1. This method will not work if an outgoing webhook is set up.
            2. In order to avoid getting duplicate updates, recalculate offset after each
               server response.
            3. To take full advantage of this library take a look at :class:`telegram.ext.Updater`

        Returns:
            List[:class:`telegram.Update`]

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getUpdates'.format(self.base_url)

        data = {'timeout': timeout}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates
        data.update(kwargs)

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
    def set_webhook(self,
                    url=None,
                    certificate=None,
                    timeout=None,
                    max_connections=40,
                    allowed_updates=None,
                    **kwargs):
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Whenever there is an update for the bot, we will send an HTTPS POST request to the
        specified url, containing a JSON-serialized Update. In case of an unsuccessful request,
        we will give up after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook request comes from Telegram, we recommend
        using a secret path in the URL, e.g. https://www.example.com/<token>. Since nobody else
        knows your bot's token, you can be pretty sure it's us.

        Note:
            The certificate argument should be a file from disk ``open(filename, 'rb')``.

        Args:
            url (:obj:`str`): HTTPS url to send updates to. Use an empty string to remove webhook
                integration.
            certificate (:obj:`filelike`): Upload your public key certificate so that the root
                certificate in use can be checked. See our self-signed guide for details.
                (https://goo.gl/rw7w6Y)
            max_connections (:obj:`int`, optional): Maximum allowed number of simultaneous HTTPS
                connections to the webhook for update delivery, 1-100. Defaults to 40. Use lower
                values to limit the load on your bot's server, and higher values to increase your
                bot's throughput.
            allowed_updates (List[:obj:`str`], optional): List the types of updates you want your
                bot to receive. For example, specify ["message", "edited_channel_post",
                "callback_query"] to only receive updates of these types. See
                :class:`telegram.Update` for a complete list of available update types. Specify an
                empty list to receive all updates regardless of type (default). If not specified,
                the previous setting will be used. Please note that this parameter doesn't affect
                updates created before the call to the set_webhook, so unwanted updates may be
                received for a short period of time.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Note:
            1. You will not be able to receive updates using get_updates for as long as an outgoing
               webhook is set up.
            2. To use a self-signed certificate, you need to upload your public key certificate
               using certificate parameter. Please upload as InputFile, sending a String will not
               work.
            3. Ports currently supported for Webhooks: 443, 80, 88, 8443.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url_ = '{0}/setWebhook'.format(self.base_url)

        # Backwards-compatibility: 'url' used to be named 'webhook_url'
        if 'webhook_url' in kwargs:  # pragma: no cover
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
            if InputFile.is_file(certificate):
                certificate = InputFile(certificate)
            data['certificate'] = certificate
        if max_connections is not None:
            data['max_connections'] = max_connections
        if allowed_updates is not None:
            data['allowed_updates'] = allowed_updates
        data.update(kwargs)

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    def delete_webhook(self, timeout=None, **kwargs):
        """
        Use this method to remove webhook integration if you decide to switch back to
        getUpdates. Requires no parameters.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/deleteWebhook'.format(self.base_url)

        data = kwargs

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def leave_chat(self, chat_id, timeout=None, **kwargs):
        """Use this method for your bot to leave a group, supergroup or channel.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool` On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/leaveChat'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def get_chat(self, chat_id, timeout=None, **kwargs):
        """
        Use this method to get up to date information about the chat (current name of the user for
        one-on-one conversations, current username of a user, group or channel, etc.).

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Chat`

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChat'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return Chat.de_json(result, self)

    @log
    def get_chat_administrators(self, chat_id, timeout=None, **kwargs):
        """
        Use this method to get a list of administrators in a chat. On success, returns an Array of
        ChatMember objects that contains information about all chat administrators except other
        bots. If the chat is a group or a supergroup and no administrators were appointed,
        only the creator will be returned.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            List[:class:`telegram.ChatMember`]

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatAdministrators'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return [ChatMember.de_json(x, self) for x in result]

    @log
    def get_chat_members_count(self, chat_id, timeout=None, **kwargs):
        """Use this method to get the number of members in a chat

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            int: Number of members in the chat.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatMembersCount'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def get_chat_member(self, chat_id, user_id, timeout=None, **kwargs):
        """Use this method to get information about a member of a chat.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.ChatMember`

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return ChatMember.de_json(result, self)

    @log
    def set_chat_sticker_set(self, chat_id, sticker_set_name, timeout=None, **kwargs):
        """Use this method to set a new group sticker set for a supergroup.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights. Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned
        in :attr:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            sticker_set_name (:obj:`str`): Name of the sticker set to be set as the group
                sticker set.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.


        Returns:
            :obj:`bool`: True on success.
        """

        url = '{0}/setChatStickerSet'.format(self.base_url)

        data = {'chat_id': chat_id, 'sticker_set_name': sticker_set_name}

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def delete_chat_sticker_set(self, chat_id, timeout=None, **kwargs):
        """Use this method to delete a group sticker set from a supergroup. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.
        Use the field :attr:`telegram.Chat.can_set_sticker_set` optionally returned in
        :attr:`get_chat` requests to check if the bot can use this method.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
             :obj:`bool`: True on success.
        """

        url = '{0}/deleteChatStickerSet'.format(self.base_url)

        data = {'chat_id': chat_id}

        result = self._request.post(url, data, timeout=timeout)

        return result

    def get_webhook_info(self, timeout=None, **kwargs):
        """Use this method to get current webhook status. Requires no parameters.

        If the bot is using getUpdates, will return an object with the url field empty.

        Args:
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.WebhookInfo`

        """
        url = '{0}/getWebhookInfo'.format(self.base_url)

        data = kwargs

        result = self._request.post(url, data, timeout=timeout)

        return WebhookInfo.de_json(result, self)

    @log
    @message
    def set_game_score(self,
                       user_id,
                       score,
                       chat_id=None,
                       message_id=None,
                       inline_message_id=None,
                       force=None,
                       disable_edit_message=None,
                       timeout=None,
                       **kwargs):
        """
        Use this method to set the score of the specified user in a game. On success, if the
        message was sent by the bot, returns the edited Message, otherwise returns True. Returns
        an error, if the new score is not greater than the user's current score in the chat and
        force is False.

        Args:
            user_id (:obj:`int`): User identifier.
            score (:obj:`int`): New score, must be non-negative.
            force (:obj:`bool`, optional): Pass True, if the high score is allowed to decrease.
                This can be useful when fixing mistakes or banning cheaters
            disable_edit_message (:obj:`bool`, optional): Pass True, if the game message should not
                be automatically edited to include the current scoreboard.
            chat_id (int|str, optional): Required if inline_message_id is not specified. Unique
                identifier for the target chat.
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: The edited message, or if the message wasn't sent by the bot
            , ``True``.

        Raises:
            :class:`telegram.TelegramError`: If the new score is not greater than the user's
            current score in the chat and force is False.

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

        return url, data

    @log
    def get_game_high_scores(self,
                             user_id,
                             chat_id=None,
                             message_id=None,
                             inline_message_id=None,
                             timeout=None,
                             **kwargs):
        """
        Use this method to get data for high score tables. Will return the score of the specified
        user and several of his neighbors in a game

        Args:
            user_id (:obj:`int`): User identifier.
            chat_id (:obj:`int` | :obj:`str`, optional): Required if inline_message_id is not
                specified. Unique identifier for the target chat.
            message_id (:obj:`int`, optional): Required if inline_message_id is not specified.
                Identifier of the sent message.
            inline_message_id (:obj:`str`, optional): Required if chat_id and message_id are not
                specified. Identifier of the inline message.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            List[:class:`telegram.GameHighScore`]

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getGameHighScores'.format(self.base_url)

        data = {'user_id': user_id}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return [GameHighScore.de_json(hs, self) for hs in result]

    @log
    @message
    def send_invoice(self,
                     chat_id,
                     title,
                     description,
                     payload,
                     provider_token,
                     start_parameter,
                     currency,
                     prices,
                     photo_url=None,
                     photo_size=None,
                     photo_width=None,
                     photo_height=None,
                     need_name=None,
                     need_phone_number=None,
                     need_email=None,
                     need_shipping_address=None,
                     is_flexible=None,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     provider_data=None,
                     send_phone_number_to_provider=None,
                     send_email_to_provider=None,
                     timeout=None,
                     **kwargs):
        """Use this method to send invoices.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target private chat.
            title (:obj:`str`): Product name.
            description (:obj:`str`): Product description.
            payload (:obj:`str`): Bot-defined invoice payload, 1-128 bytes. This will not be
                displayed to the user, use for your internal processes.
            provider_token (:obj:`str`): Payments provider token, obtained via Botfather.
            start_parameter (:obj:`str`): Unique deep-linking parameter that can be used to
                generate this invoice when used as a start parameter.
            currency (:obj:`str`): Three-letter ISO 4217 currency code.
            prices (List[:class:`telegram.LabeledPrice`)]: Price breakdown, a list of components
                (e.g. product price, tax, discount, delivery cost, delivery tax, bonus, etc.).
            provider_data (:obj:`str` | :obj:`object`, optional): JSON-encoded data about the
                invoice, which will be shared with the payment provider. A detailed description of
                required fields should be provided by the payment provider. When an object is
                passed, it will be encoded as JSON.
            photo_url (:obj:`str`, optional): URL of the product photo for the invoice. Can be a
                photo of the goods or a marketing image for a service. People like it better when
                they see what they are paying for.
            photo_size (:obj:`str`, optional): Photo size.
            photo_width (:obj:`int`, optional): Photo width.
            photo_height (:obj:`int`, optional): Photo height.
            need_name (:obj:`bool`, optional): Pass True, if you require the user's full name to
                complete the order.
            need_phone_number (:obj:`bool`, optional): Pass True, if you require the user's
                phone number to complete the order.
            need_email (:obj:`bool`, optional): Pass True, if you require the user's email to
                complete the order.
            need_shipping_address (:obj:`bool`, optional): Pass True, if you require the user's
                shipping address to complete the order.
            send_phone_number_to_provider (:obj:`bool`, optional): Pass True, if user's phone
                number should be sent to provider.
            send_email_to_provider (:obj:`bool`, optional): Pass True, if user's email address
                should be sent to provider.
            is_flexible (:obj:`bool`, optional): Pass True, if the final price depends on the
                shipping method.
            disable_notification (:obj:`bool`, optional): Sends the message silently. Users will
                receive a notification with no sound.
            reply_to_message_id (:obj:`int`, optional): If the message is a reply, ID of the
                original message.
            reply_markup (:class:`telegram.ReplyMarkup`, optional): Additional interface options.
                An inlinekeyboard. If empty, one 'Pay total price' button will be shown.
                If not empty, the first button must be a Pay button.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.Message`: On success, the sent Message is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/sendInvoice'.format(self.base_url)

        data = {
            'chat_id': chat_id,
            'title': title,
            'description': description,
            'payload': payload,
            'provider_token': provider_token,
            'start_parameter': start_parameter,
            'currency': currency,
            'prices': [p.to_dict() for p in prices]
        }
        if provider_data is not None:
            if isinstance(provider_data, string_types):
                data['provider_data'] = provider_data
            else:
                data['provider_data'] = json.dumps(provider_data)
        if photo_url is not None:
            data['photo_url'] = photo_url
        if photo_size is not None:
            data['photo_size'] = photo_size
        if photo_width is not None:
            data['photo_width'] = photo_width
        if photo_height is not None:
            data['photo_height'] = photo_height
        if need_name is not None:
            data['need_name'] = need_name
        if need_phone_number is not None:
            data['need_phone_number'] = need_phone_number
        if need_email is not None:
            data['need_email'] = need_email
        if need_shipping_address is not None:
            data['need_shipping_address'] = need_shipping_address
        if is_flexible is not None:
            data['is_flexible'] = is_flexible
        if send_phone_number_to_provider is not None:
            data['send_phone_number_to_provider'] = send_email_to_provider
        if send_email_to_provider is not None:
            data['send_email_to_provider'] = send_email_to_provider

        return url, data

    @log
    def answer_shipping_query(self,
                              shipping_query_id,
                              ok,
                              shipping_options=None,
                              error_message=None,
                              timeout=None,
                              **kwargs):
        """
        If you sent an invoice requesting a shipping address and the parameter is_flexible was
        specified, the Bot API will send an Update with a shipping_query field to the bot. Use
        this method to reply to shipping queries.

        Args:
            shipping_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify True if delivery to the specified address is possible and
                False if there are any problems (for example, if delivery to the specified address
                is not possible).
            shipping_options (List[:class:`telegram.ShippingOption`]), optional]: Required if ok is
                True. A JSON-serialized array of available shipping options.
            error_message (:obj:`str`, optional): Required if ok is False. Error message in
                human readable form that explains why it is impossible to complete the order (e.g.
                "Sorry, delivery to your desired address is unavailable"). Telegram will display
                this message to the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`; On success, True is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        ok = bool(ok)

        if ok and (shipping_options is None or error_message is not None):
            raise TelegramError(
                'answerShippingQuery: If ok is True, shipping_options '
                'should not be empty and there should not be error_message')

        if not ok and (shipping_options is not None or error_message is None):
            raise TelegramError(
                'answerShippingQuery: If ok is False, error_message '
                'should not be empty and there should not be shipping_options')

        url_ = '{0}/answerShippingQuery'.format(self.base_url)

        data = {'shipping_query_id': shipping_query_id, 'ok': ok}

        if ok:
            data['shipping_options'] = [option.to_dict() for option in shipping_options]
        if error_message is not None:
            data['error_message'] = error_message
        data.update(kwargs)

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    def answer_pre_checkout_query(self, pre_checkout_query_id, ok,
                                  error_message=None, timeout=None, **kwargs):
        """
        Once the user has confirmed their payment and shipping details, the Bot API sends the final
        confirmation in the form of an Update with the field pre_checkout_query. Use this method to
        respond to such pre-checkout queries.

        Note:
            The Bot API must receive an answer within 10 seconds after the pre-checkout
            query was sent.

        Args:
            pre_checkout_query_id (:obj:`str`): Unique identifier for the query to be answered.
            ok (:obj:`bool`): Specify True if everything is alright (goods are available, etc.) and
                the bot is ready to proceed with the order. Use False if there are any problems.
            error_message (:obj:`str`, optional): Required if ok is False. Error message in  human
                readable form that explains the reason for failure to proceed with the checkout
                (e.g. "Sorry, somebody just bought the last of our amazing black T-shirts while you
                were busy filling out your payment details. Please choose a different color or
                garment!"). Telegram will display this message to the user.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        ok = bool(ok)

        if not (ok ^ (error_message is not None)):
            raise TelegramError(
                'answerPreCheckoutQuery: If ok is True, there should '
                'not be error_message; if ok is False, error_message '
                'should not be empty')

        url_ = '{0}/answerPreCheckoutQuery'.format(self.base_url)

        data = {'pre_checkout_query_id': pre_checkout_query_id, 'ok': ok}

        if error_message is not None:
            data['error_message'] = error_message
        data.update(kwargs)

        result = self._request.post(url_, data, timeout=timeout)

        return result

    @log
    def restrict_chat_member(self, chat_id, user_id, until_date=None, can_send_messages=None,
                             can_send_media_messages=None, can_send_other_messages=None,
                             can_add_web_page_previews=None, timeout=None, **kwargs):
        """
        Use this method to restrict a user in a supergroup. The bot must be an administrator in
        the supergroup for this to work and must have the appropriate admin rights. Pass True for
        all boolean parameters to lift restrictions from a user.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            until_date (:obj:`int` | :obj:`datetime.datetime`, optional): Date when restrictions
                will be lifted for the user, unix time. If user is restricted for more than 366
                days or less than 30 seconds from the current time, they are considered to be
                restricted forever.
            can_send_messages (:obj:`bool`, optional): Pass True, if the user can send text
                messages, contacts, locations and venues.
            can_send_media_messages (:obj:`bool`, optional): Pass True, if the user can send
                audios, documents, photos, videos, video notes and voice notes, implies
                can_send_messages.
            can_send_other_messages (:obj:`bool`, optional): Pass True, if the user can send
                animations, games, stickers and use inline bots, implies can_send_media_messages.
            can_add_web_page_previews (:obj:`bool`, optional): Pass True, if the user may add
                web page previews to their messages, implies can_send_media_messages.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`bool`: Returns True on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/restrictChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        if until_date is not None:
            if isinstance(until_date, datetime):
                until_date = to_timestamp(until_date)
            data['until_date'] = until_date
        if can_send_messages is not None:
            data['can_send_messages'] = can_send_messages
        if can_send_media_messages is not None:
            data['can_send_media_messages'] = can_send_media_messages
        if can_send_other_messages is not None:
            data['can_send_other_messages'] = can_send_other_messages
        if can_add_web_page_previews is not None:
            data['can_add_web_page_previews'] = can_add_web_page_previews
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def promote_chat_member(self, chat_id, user_id, can_change_info=None,
                            can_post_messages=None, can_edit_messages=None,
                            can_delete_messages=None, can_invite_users=None,
                            can_restrict_members=None, can_pin_messages=None,
                            can_promote_members=None, timeout=None, **kwargs):
        """
        Use this method to promote or demote a user in a supergroup or a channel. The bot must be
        an administrator in the chat for this to work and must have the appropriate admin rights.
        Pass False for all boolean parameters to demote a user

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target supergroup (in the format @supergroupusername).
            user_id (:obj:`int`): Unique identifier of the target user.
            can_change_info (:obj:`bool`, optional): Pass True, if the administrator can change
                chat title, photo and other settings.
            can_post_messages (:obj:`bool`, optional): Pass True, if the administrator can
                create channel posts, channels only.
            can_edit_messages (:obj:`bool`, optional): Pass True, if the administrator can edit
                messages of other users, channels only.
            can_delete_messages (:obj:`bool`, optional): Pass True, if the administrator can
                delete messages of other users.
            can_invite_users (:obj:`bool`, optional): Pass True, if the administrator can invite
                new users to the chat.
            can_restrict_members (:obj:`bool`, optional): Pass True, if the administrator can
                restrict, ban or unban chat members.
            can_pin_messages (:obj:`bool`, optional): Pass True, if the administrator can pin
                messages, supergroups only.
            can_promote_members (:obj:`bool`, optional): Pass True, if the administrator can add
                new administrators with a subset of his own privileges or demote administrators
                that he has promoted, directly or indirectly (promoted by administrators that were
                appointed by him).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`bool`: Returns True on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/promoteChatMember'.format(self.base_url)

        data = {'chat_id': chat_id, 'user_id': user_id}

        if can_change_info is not None:
            data['can_change_info'] = can_change_info
        if can_post_messages is not None:
            data['can_post_messages'] = can_post_messages
        if can_edit_messages is not None:
            data['can_edit_messages'] = can_edit_messages
        if can_delete_messages is not None:
            data['can_delete_messages'] = can_delete_messages
        if can_invite_users is not None:
            data['can_invite_users'] = can_invite_users
        if can_restrict_members is not None:
            data['can_restrict_members'] = can_restrict_members
        if can_pin_messages is not None:
            data['can_pin_messages'] = can_pin_messages
        if can_promote_members is not None:
            data['can_promote_members'] = can_promote_members
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def export_chat_invite_link(self, chat_id, timeout=None, **kwargs):
        """
        Use this method to export an invite link to a supergroup or a channel. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`str`: Exported invite link on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/exportChatInviteLink'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def set_chat_photo(self, chat_id, photo, timeout=None, **kwargs):
        """Use this method to set a new profile photo for the chat.

        Photos can't be changed for private chats. The bot must be an administrator in the chat
        for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            photo (`filelike object`): New chat photo.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Note:
            In regular groups (non-supergroups), this method will only work if the
            'All Members Are Admins' setting is off in the target group.

        Returns:
            :obj:`bool`: Returns True on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/setChatPhoto'.format(self.base_url)

        if InputFile.is_file(photo):
            photo = InputFile(photo)

        data = {'chat_id': chat_id, 'photo': photo}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def delete_chat_photo(self, chat_id, timeout=None, **kwargs):
        """
        Use this method to delete a chat photo. Photos can't be changed for private chats. The bot
        must be an administrator in the chat for this to work and must have the appropriate admin
        rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Note:
            In regular groups (non-supergroups), this method will only work if the
            'All Members Are Admins' setting is off in the target group.

        Returns:
            :obj:`bool`: Returns ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/deleteChatPhoto'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def set_chat_title(self, chat_id, title, timeout=None, **kwargs):
        """
        Use this method to change the title of a chat. Titles can't be changed for private chats.
        The bot must be an administrator in the chat for this to work and must have the appropriate
        admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            title (:obj:`str`): New chat title, 1-255 characters.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Note:
            In regular groups (non-supergroups), this method will only work if the
            'All Members Are Admins' setting is off in the target group.

        Returns:
            :obj:`bool`: Returns ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/setChatTitle'.format(self.base_url)

        data = {'chat_id': chat_id, 'title': title}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def set_chat_description(self, chat_id, description, timeout=None, **kwargs):
        """
        Use this method to change the description of a supergroup or a channel. The bot must be an
        administrator in the chat for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            description (:obj:`str`): New chat description, 1-255 characters.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`bool`: Returns ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/setChatDescription'.format(self.base_url)

        data = {'chat_id': chat_id, 'description': description}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def pin_chat_message(self, chat_id, message_id, disable_notification=None, timeout=None,
                         **kwargs):
        """
        Use this method to pin a message in a supergroup. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            message_id (:obj:`int`): Identifier of a message to pin.
            disable_notification (:obj:`bool`, optional): Pass True, if it is not necessary to send
                a notification to all group members about the new pinned message.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`bool`: Returns ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/pinChatMessage'.format(self.base_url)

        data = {'chat_id': chat_id, 'message_id': message_id}

        if disable_notification is not None:
            data['disable_notification'] = disable_notification
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def unpin_chat_message(self, chat_id, timeout=None, **kwargs):
        """
        Use this method to unpin a message in a supergroup. The bot must be an administrator in the
        chat for this to work and must have the appropriate admin rights.

        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target`channel (in the format @channelusername).
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during creation of
                the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments

        Returns:
            :obj:`bool`: Returns ``True`` on success.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/unpinChatMessage'.format(self.base_url)

        data = {'chat_id': chat_id}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def get_sticker_set(self, name, timeout=None, **kwargs):
        """Use this method to get a sticker set.

        Args:
            name (:obj:`str`): Short name of the sticker set that is used in t.me/addstickers/
                URLs (e.g., animals)
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.StickerSet`

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/getStickerSet'.format(self.base_url)

        data = {'name': name}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return StickerSet.de_json(result, self)

    @log
    def upload_sticker_file(self, user_id, png_sticker, timeout=None, **kwargs):
        """
        Use this method to upload a .png file with a sticker for later use in
        :attr:`create_new_sticker_set` and :attr:`add_sticker_to_set` methods (can be used multiple
        times).

        Note:
            The png_sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            user_id (:obj:`int`): User identifier of sticker file owner.
            png_sticker (:obj:`str` | `filelike object`): Png image with the sticker,
                must be up to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :class:`telegram.File`: The uploaded File

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/uploadStickerFile'.format(self.base_url)

        if InputFile.is_file(png_sticker):
            png_sticker = InputFile(png_sticker)

        data = {'user_id': user_id, 'png_sticker': png_sticker}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return File.de_json(result, self)

    @log
    def create_new_sticker_set(self, user_id, name, title, png_sticker, emojis,
                               contains_masks=None, mask_position=None, timeout=None, **kwargs):
        """Use this method to create new sticker set owned by a user.

        The bot will be able to edit the created sticker set.

        Note:
            The png_sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Short name of sticker set, to be used in t.me/addstickers/ URLs
                (e.g., animals). Can contain only english letters, digits and underscores.
                Must begin with a letter, can't contain consecutive underscores and
                must end in "_by_<bot username>". <bot_username> is case insensitive.
                1-64 characters.
            title (:obj:`str`): Sticker set title, 1-64 characters.
            png_sticker (:obj:`str` | `filelike object`): Png image with the sticker, must be up
                to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px. Pass a file_id as a String to
                send a file that already exists on the Telegram servers, pass an HTTP URL as a
                String for Telegram to get a file from the Internet, or upload a new one
                using multipart/form-data.
            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            contains_masks (:obj:`bool`, optional): Pass True, if a set of mask stickers should be
                created.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should be placed on faces.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/createNewStickerSet'.format(self.base_url)

        if InputFile.is_file(png_sticker):
            png_sticker = InputFile(png_sticker)

        data = {'user_id': user_id, 'name': name, 'title': title, 'png_sticker': png_sticker,
                'emojis': emojis}

        if contains_masks is not None:
            data['contains_masks'] = contains_masks
        if mask_position is not None:
            data['mask_position'] = mask_position
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def add_sticker_to_set(self, user_id, name, png_sticker, emojis, mask_position=None,
                           timeout=None, **kwargs):
        """Use this method to add a new sticker to a set created by the bot.

        Note:
            The png_sticker argument can be either a file_id, an URL or a file from disk
            ``open(filename, 'rb')``

        Args:
            user_id (:obj:`int`): User identifier of created sticker set owner.
            name (:obj:`str`): Sticker set name.
            png_sticker (:obj:`str` | `filelike object`): Png image with the sticker, must be up
                to 512 kilobytes in size, dimensions must not exceed 512px,
                and either width or height must be exactly 512px. Pass a file_id as a String to
                send a file that already exists on the Telegram servers, pass an HTTP URL as a
                String for Telegram to get a file from the Internet, or upload a new one
                using multipart/form-data.
            emojis (:obj:`str`): One or more emoji corresponding to the sticker.
            mask_position (:class:`telegram.MaskPosition`, optional): Position where the mask
                should beplaced on faces.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/addStickerToSet'.format(self.base_url)

        if InputFile.is_file(png_sticker):
            png_sticker = InputFile(png_sticker)

        data = {'user_id': user_id, 'name': name, 'png_sticker': png_sticker, 'emojis': emojis}

        if mask_position is not None:
            data['mask_position'] = mask_position
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def set_sticker_position_in_set(self, sticker, position, timeout=None, **kwargs):
        """Use this method to move a sticker in a set created by the bot to a specific position.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            position (:obj:`int`): New sticker position in the set, zero-based.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/setStickerPositionInSet'.format(self.base_url)

        data = {'sticker': sticker, 'position': position}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def delete_sticker_from_set(self, sticker, timeout=None, **kwargs):
        """Use this method to delete a sticker from a set created by the bot.

        Args:
            sticker (:obj:`str`): File identifier of the sticker.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url = '{0}/deleteStickerFromSet'.format(self.base_url)

        data = {'sticker': sticker}
        data.update(kwargs)

        result = self._request.post(url, data, timeout=timeout)

        return result

    @log
    def set_passport_data_errors(self, user_id, errors, timeout=None, **kwargs):
        """
        Informs a user that some of the Telegram Passport elements they provided contains errors.
        The user will not be able to re-submit their Passport to you until the errors are fixed
        (the contents of the field for which you returned the error must change). Returns True
        on success.

        Use this if the data submitted by the user doesn't satisfy the standards your service
        requires for any reason. For example, if a birthday date seems invalid, a submitted
        document is blurry, a scan shows evidence of tampering, etc. Supply some details in the
        error message to make sure the user knows how to correct the issues.

        Args:
            user_id (:obj:`int`): User identifier
            errors (List[:class:`PassportElementError`]): A JSON-serialized array describing the
                errors.
            timeout (:obj:`int` | :obj:`float`, optional): If this value is specified, use it as
                the read timeout from the server (instead of the one specified during
                creation of the connection pool).
            **kwargs (:obj:`dict`): Arbitrary keyword arguments.

        Returns:
            :obj:`bool`: On success, ``True`` is returned.

        Raises:
            :class:`telegram.TelegramError`

        """
        url_ = '{0}/setPassportDataErrors'.format(self.base_url)

        data = {'user_id': user_id, 'errors': [error.to_dict() for error in errors]}
        data.update(kwargs)

        result = self._request.post(url_, data, timeout=timeout)

        return result

    def to_dict(self):
        data = {'id': self.id, 'username': self.username, 'first_name': self.username}

        if self.last_name:
            data['last_name'] = self.last_name

        return data

    def __reduce__(self):
        return (self.__class__, (self.token, self.base_url.replace(self.token, ''),
                                 self.base_file_url.replace(self.token, '')))

    # camelCase aliases
    getMe = get_me
    """Alias for :attr:`get_me`"""
    sendMessage = send_message
    """Alias for :attr:`send_message`"""
    deleteMessage = delete_message
    """Alias for :attr:`delete_message`"""
    forwardMessage = forward_message
    """Alias for :attr:`forward_message`"""
    sendPhoto = send_photo
    """Alias for :attr:`send_photo`"""
    sendAudio = send_audio
    """Alias for :attr:`send_audio`"""
    sendDocument = send_document
    """Alias for :attr:`send_document`"""
    sendSticker = send_sticker
    """Alias for :attr:`send_sticker`"""
    sendVideo = send_video
    """Alias for :attr:`send_video`"""
    sendAnimation = send_animation
    """Alias for :attr:`send_animation`"""
    sendVoice = send_voice
    """Alias for :attr:`send_voice`"""
    sendVideoNote = send_video_note
    """Alias for :attr:`send_video_note`"""
    sendMediaGroup = send_media_group
    """Alias for :attr:`send_media_group`"""
    sendLocation = send_location
    """Alias for :attr:`send_location`"""
    editMessageLiveLocation = edit_message_live_location
    """Alias for :attr:`edit_message_live_location`"""
    stopMessageLiveLocation = stop_message_live_location
    """Alias for :attr:`stop_message_live_location`"""
    sendVenue = send_venue
    """Alias for :attr:`send_venue`"""
    sendContact = send_contact
    """Alias for :attr:`send_contact`"""
    sendGame = send_game
    """Alias for :attr:`send_game`"""
    sendChatAction = send_chat_action
    """Alias for :attr:`send_chat_action`"""
    answerInlineQuery = answer_inline_query
    """Alias for :attr:`answer_inline_query`"""
    getUserProfilePhotos = get_user_profile_photos
    """Alias for :attr:`get_user_profile_photos`"""
    getFile = get_file
    """Alias for :attr:`get_file`"""
    kickChatMember = kick_chat_member
    """Alias for :attr:`kick_chat_member`"""
    unbanChatMember = unban_chat_member
    """Alias for :attr:`unban_chat_member`"""
    answerCallbackQuery = answer_callback_query
    """Alias for :attr:`answer_callback_query`"""
    editMessageText = edit_message_text
    """Alias for :attr:`edit_message_text`"""
    editMessageCaption = edit_message_caption
    """Alias for :attr:`edit_message_caption`"""
    editMessageMedia = edit_message_media
    """Alias for :attr:`edit_message_media`"""
    editMessageReplyMarkup = edit_message_reply_markup
    """Alias for :attr:`edit_message_reply_markup`"""
    getUpdates = get_updates
    """Alias for :attr:`get_updates`"""
    setWebhook = set_webhook
    """Alias for :attr:`set_webhook`"""
    deleteWebhook = delete_webhook
    """Alias for :attr:`delete_webhook`"""
    leaveChat = leave_chat
    """Alias for :attr:`leave_chat`"""
    getChat = get_chat
    """Alias for :attr:`get_chat`"""
    getChatAdministrators = get_chat_administrators
    """Alias for :attr:`get_chat_administrators`"""
    getChatMember = get_chat_member
    """Alias for :attr:`get_chat_member`"""
    setChatStickerSet = set_chat_sticker_set
    """Alias for :attr:`set_chat_sticker_set`"""
    deleteChatStickerSet = delete_chat_sticker_set
    """Alias for :attr:`delete_chat_sticker_set`"""
    getChatMembersCount = get_chat_members_count
    """Alias for :attr:`get_chat_members_count`"""
    getWebhookInfo = get_webhook_info
    """Alias for :attr:`get_webhook_info`"""
    setGameScore = set_game_score
    """Alias for :attr:`set_game_score`"""
    getGameHighScores = get_game_high_scores
    """Alias for :attr:`get_game_high_scores`"""
    sendInvoice = send_invoice
    """Alias for :attr:`send_invoice`"""
    answerShippingQuery = answer_shipping_query
    """Alias for :attr:`answer_shipping_query`"""
    answerPreCheckoutQuery = answer_pre_checkout_query
    """Alias for :attr:`answer_pre_checkout_query`"""
    restrictChatMember = restrict_chat_member
    """Alias for :attr:`restrict_chat_member`"""
    promoteChatMember = promote_chat_member
    """Alias for :attr:`promote_chat_member`"""
    exportChatInviteLink = export_chat_invite_link
    """Alias for :attr:`export_chat_invite_link`"""
    setChatPhoto = set_chat_photo
    """Alias for :attr:`set_chat_photo`"""
    deleteChatPhoto = delete_chat_photo
    """Alias for :attr:`delete_chat_photo`"""
    setChatTitle = set_chat_title
    """Alias for :attr:`set_chat_title`"""
    setChatDescription = set_chat_description
    """Alias for :attr:`set_chat_description`"""
    pinChatMessage = pin_chat_message
    """Alias for :attr:`pin_chat_message`"""
    unpinChatMessage = unpin_chat_message
    """Alias for :attr:`unpin_chat_message`"""
    getStickerSet = get_sticker_set
    """Alias for :attr:`get_sticker_set`"""
    uploadStickerFile = upload_sticker_file
    """Alias for :attr:`upload_sticker_file`"""
    createNewStickerSet = create_new_sticker_set
    """Alias for :attr:`create_new_sticker_set`"""
    addStickerToSet = add_sticker_to_set
    """Alias for :attr:`add_sticker_to_set`"""
    setStickerPositionInSet = set_sticker_position_in_set
    """Alias for :attr:`set_sticker_position_in_set`"""
    deleteStickerFromSet = delete_sticker_from_set
    """Alias for :attr:`delete_sticker_from_set`"""
    setPassportDataErrors = set_passport_data_errors
    """Alias for :attr:`set_passport_data_errors`"""
