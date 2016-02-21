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
from telegram.utils.validate import validate_string


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
                 parse_mode=None,
                 disable_web_page_preview=None,
                 url=None,
                 hide_url=None,
                 description=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None):

        validate_string(title, 'title')
        validate_string(message_text, 'message_text')
        validate_string(url, 'url')
        validate_string(description, 'description')
        validate_string(thumb_url, 'thumb_url')
        validate_string(parse_mode, 'parse_mode')

        # Required
        super(InlineQueryResultArticle, self).__init__('article', id)
        self.title = title
        self.message_text = message_text

        # Optional
        self.parse_mode = parse_mode
        self.disable_web_page_preview = bool(disable_web_page_preview)
        self.url = url
        self.hide_url = bool(hide_url)
        self.description = description
        self.thumb_url = thumb_url
        if thumb_width is not None:
            self.thumb_width = int(thumb_width)
        if thumb_height is not None:
            self.thumb_height = int(thumb_height)

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
        data = data.copy()
        data.pop('type', None)

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
                 mime_type=None,
                 photo_width=None,
                 photo_height=None,
                 title=None,
                 description=None,
                 caption=None,
                 message_text=None,
                 parse_mode=None,
                 disable_web_page_preview=None):

        validate_string(photo_url, 'photo_url')
        validate_string(thumb_url, 'thumb_url')
        validate_string(mime_type, 'mime_type')
        validate_string(title, 'title')
        validate_string(description, 'description')
        validate_string(caption, 'caption')
        validate_string(message_text, 'message_text')
        validate_string(parse_mode, 'parse_mode')

        # Required
        super(InlineQueryResultPhoto, self).__init__('photo', id)
        self.photo_url = photo_url
        self.thumb_url = thumb_url

        # Optional
        self.mime_type = mime_type
        if photo_width is not None:
            self.photo_width = int(photo_width)
        if photo_height is not None:
            self.photo_height = int(photo_height)
        self.title = title
        self.description = description
        self.caption = caption
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = bool(disable_web_page_preview)

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
        data = data.copy()
        data.pop('type', None)

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
                 gif_width=None,
                 gif_height=None,
                 title=None,
                 caption=None,
                 message_text=None,
                 parse_mode=None,
                 disable_web_page_preview=None):

        validate_string(gif_url, 'gif_url')
        validate_string(thumb_url, 'thumb_url')
        validate_string(title, 'title')
        validate_string(caption, 'caption')
        validate_string(message_text, 'message_text')
        validate_string(parse_mode, 'parse_mode')

        # Required
        super(InlineQueryResultGif, self).__init__('gif', id)
        self.gif_url = gif_url
        self.thumb_url = thumb_url

        # Optional
        if gif_width is not None:
            self.gif_width = int(gif_width)
        if gif_height is not None:
            self.gif_height = int(gif_height)
        self.title = title
        self.caption = caption
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = bool(disable_web_page_preview)

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
        data = data.copy()
        data.pop('type', None)

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
                 mpeg4_width=None,
                 mpeg4_height=None,
                 title=None,
                 caption=None,
                 message_text=None,
                 parse_mode=None,
                 disable_web_page_preview=None):

        validate_string(mpeg4_url, 'mpeg4_url')
        validate_string(thumb_url, 'thumb_url')
        validate_string(title, 'title')
        validate_string(caption, 'caption')
        validate_string(message_text, 'message_text')
        validate_string(parse_mode, 'parse_mode')

        # Required
        super(InlineQueryResultMpeg4Gif, self).__init__('mpeg4_gif', id)
        self.mpeg4_url = mpeg4_url
        self.thumb_url = thumb_url

        # Optional
        if mpeg4_width is not None:
            self.mpeg4_width = int(mpeg4_width)
        if mpeg4_height is not None:
            self.mpeg4_height = int(mpeg4_height)
        self.title = title
        self.caption = caption
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = bool(disable_web_page_preview)

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
        data = data.copy()
        data.pop('type', None)

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
                 video_width=None,
                 video_height=None,
                 video_duration=None,
                 description=None,
                 caption=None,
                 parse_mode=None,
                 disable_web_page_preview=None):

        validate_string(video_url, 'video_url')
        validate_string(mime_type, 'mime_type')
        validate_string(thumb_url, 'thumb_url')
        validate_string(title, 'title')
        validate_string(message_text, 'message_text')
        validate_string(description, 'description')
        validate_string(caption, 'caption')
        validate_string(parse_mode, 'parse_mode')

        # Required
        super(InlineQueryResultVideo, self).__init__('video', id)
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.title = title
        self.message_text = message_text

        # Optional
        if video_width is not None:
            self.video_width = int(video_width)
        if video_height is not None:
            self.video_height = int(video_height)
        if video_duration is not None:
            self.video_duration = int(video_duration)
        self.description = description
        self.caption = caption
        self.parse_mode = parse_mode
        self.disable_web_page_preview = bool(disable_web_page_preview)

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
        data = data.copy()
        data.pop('type', None)

        return InlineQueryResultVideo(**data)
