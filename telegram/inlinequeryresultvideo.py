#!/usr/bin/env python
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

"""This module contains the classes that represent Telegram
InlineQueryResultVideo"""

from telegram import InlineQueryResult
from telegram.utils.validate import validate_string


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
                 disable_web_page_preview=None,
                 **kwargs):

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

        return InlineQueryResultVideo(**data)
