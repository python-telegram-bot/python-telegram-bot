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

from telegram import InlineQueryResult, InlineKeyboardMarkup, InputMessageContent


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Attributes:
        id (str):
        title (str):
        input_message_content (:class:`telegram.InputMessageContent`):
        reply_markup (:class:`telegram.ReplyMarkup`):
        url (str):
        hide_url (bool):
        description (str):
        thumb_url (str):
        thumb_width (int):
        thumb_height (int):

    Deprecated: 4.0
        message_text (str): Use :class:`InputTextMessageContent` instead.

        parse_mode (str): Use :class:`InputTextMessageContent` instead.

        disable_web_page_preview (bool): Use :class:`InputTextMessageContent`
        instead.

    Args:
        id (str): Unique identifier for this result, 1-64 Bytes
        title (str):
        reply_markup (:class:`telegram.ReplyMarkup`):

    Keyword Args:
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
                 input_message_content,
                 reply_markup=None,
                 url=None,
                 hide_url=None,
                 description=None,
                 thumb_url=None,
                 thumb_width=None,
                 thumb_height=None,
                 **kwargs):

        # Required
        super(InlineQueryResultArticle, self).__init__('article', id)
        self.title = title
        self.input_message_content = input_message_content

        # Optional
        if reply_markup:
            self.reply_markup = reply_markup
        if url:
            self.url = url
        if hide_url:
            self.hide_url = hide_url
        if description:
            self.description = description
        if thumb_url:
            self.thumb_url = thumb_url
        if thumb_width:
            self.thumb_width = thumb_width
        if thumb_height:
            self.thumb_height = thumb_height

    @staticmethod
    def de_json(data):
        data = super(InlineQueryResultArticle, InlineQueryResultArticle).de_json(data)

        data['reply_markup'] = InlineKeyboardMarkup.de_json(data.get('reply_markup'))
        data['input_message_content'] = InputMessageContent.de_json(data.get(
            'input_message_content'))

        return InlineQueryResultArticle(**data)
