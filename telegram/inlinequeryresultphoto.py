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
InlineQueryResultPhoto"""

from telegram import InlineQueryResult
from telegram.utils.validate import validate_string


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
