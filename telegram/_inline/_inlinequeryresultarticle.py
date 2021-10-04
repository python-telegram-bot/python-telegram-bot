#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
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

from typing import TYPE_CHECKING, Any

from telegram import InlineQueryResult

if TYPE_CHECKING:
    from telegram import InputMessageContent, ReplyMarkup


class InlineQueryResultArticle(InlineQueryResult):
    """This object represents a Telegram InlineQueryResultArticle.

    Args:
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`, optional): Inline keyboard attached to
            the message
        url (:obj:`str`, optional): URL of the result.
        hide_url (:obj:`bool`, optional): Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`, optional): Short description of the result.
        thumb_url (:obj:`str`, optional): Url of the thumbnail for the result.
        thumb_width (:obj:`int`, optional): Thumbnail width.
        thumb_height (:obj:`int`, optional): Thumbnail height.
        **kwargs (:obj:`dict`): Arbitrary keyword arguments.

    Attributes:
        type (:obj:`str`): 'article'.
        id (:obj:`str`): Unique identifier for this result, 1-64 Bytes.
        title (:obj:`str`): Title of the result.
        input_message_content (:class:`telegram.InputMessageContent`): Content of the message to
            be sent.
        reply_markup (:class:`telegram.ReplyMarkup`): Optional. Inline keyboard attached to
            the message.
        url (:obj:`str`): Optional. URL of the result.
        hide_url (:obj:`bool`): Optional. Pass :obj:`True`, if you don't want the URL to be shown
            in the message.
        description (:obj:`str`): Optional. Short description of the result.
        thumb_url (:obj:`str`): Optional. Url of the thumbnail for the result.
        thumb_width (:obj:`int`): Optional. Thumbnail width.
        thumb_height (:obj:`int`): Optional. Thumbnail height.

    """

    __slots__ = (
        'reply_markup',
        'thumb_width',
        'thumb_height',
        'hide_url',
        'url',
        'title',
        'description',
        'input_message_content',
        'thumb_url',
    )

    def __init__(
        self,
        id: str,  # pylint: disable=W0622
        title: str,
        input_message_content: 'InputMessageContent',
        reply_markup: 'ReplyMarkup' = None,
        url: str = None,
        hide_url: bool = None,
        description: str = None,
        thumb_url: str = None,
        thumb_width: int = None,
        thumb_height: int = None,
        **_kwargs: Any,
    ):

        # Required
        super().__init__('article', id)
        self.title = title
        self.input_message_content = input_message_content

        # Optional
        self.reply_markup = reply_markup
        self.url = url
        self.hide_url = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
