#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015 Leandro Toledo de Souza <devs@python-telegram-bot.org>
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

"""
This module contains the classes that represent Telegram InlineQueryResults
https://core.telegram.org/bots/api#inline-mode
"""

from telegram import TelegramObject


class InlineQueryResult(TelegramObject):
    """This object represents a Telegram InlineQueryResult.

    Attributes:
        type (str):
        id (str):

    Args:
        type (str):
        id (str): Unique identifier for this result, 1-64 Bytes

    """

    def __init__(self,
                 type,
                 id):
        # Required
        self.type = str(type)
        self.id = str(id)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResult:
        """
        if not data:
            return None

        return InlineQueryResult(**data)


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Attributes:
        id (str):
        title (str):
        message_text (str):
        parse_mode (str):
        disable_web_page_preview (bool):
        url (str):
        hide_url (bool):
        description (str):
        thumb_url (str):
        thumb_width (int):
        thumb_height (int):

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        title (str):
        message_text (str):

    Keyword Args:
        parse_mode (Optional[str]):
        disable_web_page_preview (Optional[bool]):
        url (Optional[str]):
        hide_url (Optional[bool]):
        description (Optional[str]):
        thumb_url (Optional[str]):
        thumb_width (Optional[int]):
        thumb_height (Optional[int]):
    """

    def __init__(self,
                 id,
                 title,
                 message_text,
                 **kwargs):
        # Required
        super(InlineQueryResultArticle, self).__init__('article', id)
        self.title = title
        self.message_text = message_text

        # Optional
        self.parse_mode = kwargs.get('parse_mode', '')
        self.disable_web_page_preview = kwargs.get('disable_web_page_preview',
                                                   False)
        self.url = kwargs.get('url', '')
        self.hide_url = kwargs.get('hide_url', False)
        self.description = kwargs.get('description', '')
        self.thumb_url = kwargs.get('thumb_url', '')
        self.parse_mode = kwargs.get('parse_mode', '')
        if 'thumb_width' in kwargs:
            self.thumb_width = int(kwargs['thumb_width'])
        if 'thumb_height' in kwargs:
            self.thumb_height = int(kwargs['thumb_height'])

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResultArticle:
        """
        if not data:
            return None

        return InlineQueryResultArticle(**data)


class InlineQueryResultPhoto(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultPhoto.

    Attributes:
        id (str):
        photo_url (str):
        mime_type (str):
        photo_width (int):
        photo_height (int):
        thumb_url (str):
        title (str):
        description (str):
        caption (str):
        message_text (str):
        parse_mode (str):
        disable_web_page_preview (bool):

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        photo_url (str):
        thumb_url (str):

    Keyword Args:
        mime_type (Optional[str]):
        photo_width (Optional[int]):
        photo_height (Optional[int]):
        title (Optional[str]):
        description (Optional[str]):
        caption (Optional[str]):
        message_text (Optional[str]):
        parse_mode (Optional[str]):
        disable_web_page_preview (Optional[bool]):
    """

    def __init__(self,
                 id,
                 photo_url,
                 thumb_url,
                 **kwargs):
        # Required
        super(InlineQueryResultPhoto, self).__init__('photo', id)
        self.photo_url = photo_url
        self.thumb_url = thumb_url

        # Optional
        self.mime_type = kwargs.get('mime_type', 'image/jpeg')
        if 'photo_width' in kwargs:
            self.photo_width = int(kwargs['photo_width'])
        if 'photo_height' in kwargs:
            self.photo_height = int(kwargs['photo_height'])
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.caption = kwargs.get('caption', '')
        self.message_text = kwargs.get('message_text', '')
        self.parse_mode = kwargs.get('parse_mode', '')
        self.disable_web_page_preview = kwargs.get('disable_web_page_preview',
                                                   False)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResultPhoto:
        """
        if not data:
            return None

        return InlineQueryResultPhoto(**data)


class InlineQueryResultGif(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultGif.

    Attributes:
        id (str):
        gif_url (str):
        gif_width (int):
        gif_height (int):
        thumb_url (str):
        title (str):
        caption (str):
        message_text (str):
        parse_mode (str):
        disable_web_page_preview (bool):

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        gif_url (str):
        thumb_url (str):

    Keyword Args:
        gif_width (Optional[int]):
        gif_height (Optional[int]):
        title (Optional[str]):
        caption (Optional[str]):
        message_text (Optional[str]):
        parse_mode (Optional[str]):
        disable_web_page_preview (Optional[bool]):
    """

    def __init__(self,
                 id,
                 gif_url,
                 thumb_url,
                 **kwargs):
        # Required
        super(InlineQueryResultGif, self).__init__('gif', id)
        self.gif_url = gif_url
        self.thumb_url = thumb_url

        # Optional
        if 'gif_width' in kwargs:
            self.gif_width = int(kwargs['gif_width'])
        if 'gif_height' in kwargs:
            self.gif_height = int(kwargs['gif_height'])
        self.title = kwargs.get('title', '')
        self.caption = kwargs.get('caption', '')
        self.message_text = kwargs.get('message_text', '')
        self.parse_mode = kwargs.get('parse_mode', '')
        self.disable_web_page_preview = kwargs.get('disable_web_page_preview',
                                                   False)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResultGif:
        """
        if not data:
            return None

        return InlineQueryResultGif(**data)


class InlineQueryResultMpeg4Gif(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultMpeg4Gif.

    Attributes:
        id (str):
        mpeg4_url (str):
        mpeg4_width (int):
        mpeg4_height (int):
        thumb_url (str):
        title (str):
        caption (str):
        message_text (str):
        parse_mode (str):
        disable_web_page_preview (bool):

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        mpeg4_url (str):
        thumb_url (str):

    Keyword Args:
        mpeg4_width (Optional[int]):
        mpeg4_height (Optional[int]):
        title (Optional[str]):
        caption (Optional[str]):
        message_text (Optional[str]):
        parse_mode (Optional[str]):
        disable_web_page_preview (Optional[bool]):
    """

    def __init__(self,
                 id,
                 mpeg4_url,
                 thumb_url,
                 **kwargs):
        # Required
        super(InlineQueryResultMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url

        # Optional
        if 'mpeg4_width' in kwargs:
            self.mpeg4_width = int(kwargs['mpeg4_width'])
        if 'mpeg4_height' in kwargs:
            self.mpeg4_height = int(kwargs['mpeg4_height'])
        self.title = kwargs.get('title', '')
        self.caption = kwargs.get('caption', '')
        self.message_text = kwargs.get('message_text', '')
        self.parse_mode = kwargs.get('parse_mode', '')
        self.disable_web_page_preview = kwargs.get('disable_web_page_preview',
                                                   False)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResultMpeg4Gif:
        """
        if not data:
            return None

        return InlineQueryResultMpeg4Gif(**data)


class InlineQueryResultVideo(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultVideo.

    Attributes:
        id (str):
        video_url (str):
        mime_type (str):
        video_width (int):
        video_height (int):
        video_duration (int):
        thumb_url (str):
        title (str):
        description (str):
        caption (str):
        message_text (str):
        parse_mode (str):
        disable_web_page_preview (bool):

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        video_url (str):
        mime_type (str):
        thumb_url (str):
        title (str):
        message_text (str):

    Keyword Args:
        video_width (Optional[int]):
        video_height (Optional[int]):
        video_duration (Optional[int]):
        description (Optional[str]):
        caption (Optional[str]):
        parse_mode (Optional[str]):
        disable_web_page_preview (Optional[bool]):
    """

    def __init__(self,
                 id,
                 video_url,
                 mime_type,
                 thumb_url,
                 title,
                 message_text,
                 **kwargs):
        # Required
        super(InlineQueryResultVideo, self).__init__('video', id)
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title
        self.message_text = message_text

        # Optional
        if 'video_width' in kwargs:
            self.video_width = int(kwargs['video_width'])
        if 'video_height' in kwargs:
            self.video_height = int(kwargs['video_height'])
        if 'video_duration' in kwargs:
            self.video_duration = int(kwargs['video_duration'])
        self.description = kwargs.get('description', '')
        self.caption = kwargs.get('caption', '')
        self.parse_mode = kwargs.get('parse_mode', '')
        self.disable_web_page_preview = kwargs.get('disable_web_page_preview',
                                                   False)

    @staticmethod
    def de_json(data):
        """
        Args:
            data (dict):

        Returns:
            telegram.InlineQueryResultVideo:
        """
        if not data:
            return None

        return InlineQueryResultVideo(**data)
