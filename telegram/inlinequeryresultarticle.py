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
InlineQueryResultArticle"""

from telegram import InlineQueryResult
from telegram.utils.validate import validate_string


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
                 thumb_height=None,
                 **kwargs):

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

        return InlineQueryResultArticle(**data)
