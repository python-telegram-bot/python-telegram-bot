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

from telegram import InlineQueryResult
from telegram.utils.validate import validate_string


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
