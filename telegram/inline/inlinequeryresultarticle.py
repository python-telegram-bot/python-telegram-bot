#!/usr/bin/env python
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
"""This module contains the classes that represent Telegram InlineQueryResultArticle."""

from telegram import InlineQueryResult


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Attributes:
        type (:obj:`str`): 'article'.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`): Optional. Inline keyboard attached to
            the message.
        url (:obj:`str`): Optional. URL of the result.
        hide_url (:obj:`bool`): Optional. Pass True, if you don't want the URL to be shown in the
            message.
        description (:obj:`str`): Optional. Short description of the result.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`, optional): Inline keyboard attached to
            the message
        url (:obj:`str`, optional): URL of the result.
        hide_url (:obj:`bool`, optional): Pass True, if you don't want the URL to be shown in the
            message.
        description (:obj:`str`, optional): Short description of the result.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

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
